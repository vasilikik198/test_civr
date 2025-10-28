"""
Routes module for Conversational IVR application.
Handles all Flask route definitions and HTTP request processing.
"""

import logging
from flask import render_template, request, jsonify, send_file
import io
from typing import Dict

logger = logging.getLogger(__name__)


class Routes:
    """Class to handle all Flask routes."""

    def __init__(self, app, config, speech_service, intent_service):
        """Initialize routes with Flask app and services."""
        self.app = app
        self.config = config
        self.speech_service = speech_service
        self.intent_service = intent_service
        self.conversation_sessions = {}  # Store conversation history per session
        self._register_routes()

    def _register_routes(self):
        """Register all routes with the Flask app."""

        @self.app.route("/")
        def index():
            """Home page with IVR interface."""
            return render_template("ivr.html")

        # --- Chunked streaming endpoints to simulate live transcription ---
        self.live_transcripts = {}

        @self.app.route("/api/stream/start", methods=["POST"])
        def stream_start():
            """Start a new streaming session for live-like transcription."""
            try:
                data = request.get_json(silent=True) or {}
                session_id = data.get("session_id", "default")
                self.live_transcripts[session_id] = ""
                return jsonify({"success": True, "session_id": session_id})
            except Exception as e:
                logger.error(f"Error in stream_start: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/stream/chunk", methods=["POST"])
        def stream_chunk():
            """Accept a short audio chunk, transcribe it, and append to session transcript."""
            try:
                session_id = request.form.get("session_id", "default")
                if "audio" not in request.files:
                    return jsonify({"error": "No audio file provided"}), 400

                audio_file = request.files["audio"]
                audio_data = audio_file.read()

                # Save chunk to disk for debugging
                import os
                from datetime import datetime

                base_dir = getattr(self.config, "STREAM_UPLOADS_DIR", "stream_uploads")
                session_dir = os.path.join(base_dir, session_id)
                os.makedirs(session_dir, exist_ok=True)
                chunk_name = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f") + ".wav"
                chunk_path = os.path.join(session_dir, chunk_name)

                # Transcribe this chunk (best-effort). Append if any text recognized.
                partial_text = (
                    self.speech_service.transcribe_audio_stream(
                        audio_data, save_path=chunk_path
                    )
                    or ""
                )

                if session_id not in self.live_transcripts:
                    self.live_transcripts[session_id] = ""

                if partial_text:
                    # Add a space delimiter to keep words separated
                    self.live_transcripts[session_id] = (
                        self.live_transcripts[session_id] + " " + partial_text
                    ).strip()

                return jsonify(
                    {
                        "success": True,
                        "partial": partial_text,
                        "transcript": self.live_transcripts[session_id],
                        "session_id": session_id,
                    }
                )
            except Exception as e:
                logger.error(f"Error in stream_chunk: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/stream/status", methods=["GET"])
        def stream_status():
            """Return current accumulated transcript for the session."""
            try:
                session_id = request.args.get("session_id", "default")
                transcript = self.live_transcripts.get(session_id, "")
                return jsonify(
                    {
                        "success": True,
                        "transcript": transcript,
                        "session_id": session_id,
                    }
                )
            except Exception as e:
                logger.error(f"Error in stream_status: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/stream/stop", methods=["POST"])
        def stream_stop():
            """Stop streaming and return the final accumulated transcript."""
            try:
                data = request.get_json(silent=True) or {}
                session_id = data.get("session_id", "default")
                transcript = self.live_transcripts.get(session_id, "")
                return jsonify(
                    {
                        "success": True,
                        "transcript": transcript,
                        "session_id": session_id,
                    }
                )
            except Exception as e:
                logger.error(f"Error in stream_stop: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/transcribe", methods=["POST"])
        def transcribe_audio():
            """Transcribe audio data to text."""
            try:
                # Check if audio file is in the request
                if "audio" not in request.files:
                    return jsonify({"error": "No audio file provided"}), 400

                audio_file = request.files["audio"]

                # Read audio data
                audio_data = audio_file.read()

                # Transcribe using Azure Speech Services
                transcript = self.speech_service.transcribe_audio_stream(audio_data)

                if transcript:
                    return jsonify({"success": True, "transcript": transcript})
                else:
                    return jsonify(
                        {"success": False, "error": "Could not transcribe audio"}
                    ), 500

            except Exception as e:
                logger.error(f"Error in transcribe_audio: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/synthesize", methods=["POST"])
        def synthesize_speech():
            """Convert text to speech."""
            try:
                data = request.get_json()
                text = data.get("text", "")

                if not text:
                    return jsonify({"error": "No text provided"}), 400

                # Get session ID for conversation tracking
                session_id = data.get("session_id", "default")

                # Generate speech using ElevenLabs
                audio_data = self.speech_service.text_to_speech(text)

                if audio_data:
                    return send_file(
                        io.BytesIO(audio_data),
                        mimetype="audio/mpeg",
                        as_attachment=False,
                    )
                else:
                    return jsonify({"error": "Could not synthesize speech"}), 500

            except Exception as e:
                logger.error(f"Error in synthesize_speech: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/converse", methods=["POST"])
        def converse():
            """Handle a conversational turn with intent classification and response generation."""
            try:
                data = request.get_json()
                user_message = data.get("message", "")
                session_id = data.get("session_id", "default")

                if not user_message:
                    return jsonify({"error": "No message provided"}), 400

                # Initialize conversation history if needed
                if session_id not in self.conversation_sessions:
                    self.conversation_sessions[session_id] = []

                conversation_history = self.conversation_sessions[session_id]

                # Classify intent
                intent_result = self.intent_service.classify_intent(user_message)

                # Generate response based on intent
                bot_response = self.intent_service.generate_response(
                    user_message, intent_result["intent"], conversation_history
                )

                # Update conversation history
                conversation_history.append({"role": "user", "content": user_message})
                conversation_history.append(
                    {"role": "assistant", "content": bot_response}
                )

                return jsonify(
                    {
                        "success": True,
                        "intent": intent_result["intent"],
                        "confidence": intent_result["confidence"],
                        "reasoning": intent_result.get("reasoning", ""),
                        "response": bot_response,
                    }
                )

            except Exception as e:
                logger.error(f"Error in converse: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/clear-session", methods=["POST"])
        def clear_session():
            """Clear conversation history for a session."""
            try:
                data = request.get_json()
                session_id = data.get("session_id", "default")

                if session_id in self.conversation_sessions:
                    del self.conversation_sessions[session_id]

                return jsonify({"success": True, "message": "Session cleared"})

            except Exception as e:
                logger.error(f"Error in clear_session: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.errorhandler(404)
        def not_found_error(error):
            """Handle 404 errors."""
            return jsonify({"error": "Not found"}), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors."""
            logger.error(f"Internal server error: {error}")
            return jsonify({"error": "Internal server error"}), 500
