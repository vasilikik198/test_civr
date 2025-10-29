"""
Conversational IVR - Main Flask Application
A voice-enabled IVR system with Azure Speech Services and ElevenLabs.
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import logging
import io
from src.config.config import config
from src.services.speech_service import SpeechService
from src.services.intent_service import IntentService


def create_app():
    """Application factory pattern for creating Flask app."""

    # Create Flask app
    app = Flask(__name__)
    CORS(app)

    # Configure Flask app
    app.config["SECRET_KEY"] = config.SECRET_KEY

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Conversational IVR application")

    # Initialize services
    speech_service = SpeechService(config)
    intent_service = IntentService(config)

    # In-memory session stores
    conversation_sessions = {}
    live_transcripts = {}

    # ------------------ Routes ------------------
    @app.route("/")
    def index():
        return render_template("ivr.html")

    # Chunked streaming endpoints
    @app.route("/api/stream/start", methods=["POST"])
    def stream_start():
        try:
            data = request.get_json(silent=True) or {}
            session_id = data.get("session_id", "default")
            live_transcripts[session_id] = ""
            return jsonify({"success": True, "session_id": session_id})
        except Exception as e:
            logging.error(f"Error in stream_start: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/stream/chunk", methods=["POST"])
    def stream_chunk():
        try:
            session_id = request.form.get("session_id", "default")
            if "audio" not in request.files:
                return jsonify({"error": "No audio file provided"}), 400

            audio_file = request.files["audio"]
            audio_data = audio_file.read()

            # Save chunk to disk for debugging
            import os
            from datetime import datetime
            base_dir = getattr(config, "STREAM_UPLOADS_DIR", "stream_uploads")
            session_dir = os.path.join(base_dir, session_id)
            os.makedirs(session_dir, exist_ok=True)
            chunk_name = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f") + ".wav"
            chunk_path = os.path.join(session_dir, chunk_name)

            # Transcribe chunk and accumulate
            partial_text = (
                speech_service.transcribe_audio_stream(audio_data, save_path=chunk_path)
                or ""
            )

            if session_id not in live_transcripts:
                live_transcripts[session_id] = ""

            if partial_text:
                live_transcripts[session_id] = (
                    live_transcripts[session_id] + " " + partial_text
                ).strip()

            return jsonify(
                {
                    "success": True,
                    "partial": partial_text,
                    "transcript": live_transcripts[session_id],
                    "session_id": session_id,
                }
            )
        except Exception as e:
            logging.error(f"Error in stream_chunk: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/stream/status", methods=["GET"])
    def stream_status():
        try:
            session_id = request.args.get("session_id", "default")
            transcript = live_transcripts.get(session_id, "")
            return jsonify(
                {"success": True, "transcript": transcript, "session_id": session_id}
            )
        except Exception as e:
            logging.error(f"Error in stream_status: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/stream/stop", methods=["POST"])
    def stream_stop():
        try:
            data = request.get_json(silent=True) or {}
            session_id = data.get("session_id", "default")
            transcript = live_transcripts.get(session_id, "")
            return jsonify(
                {"success": True, "transcript": transcript, "session_id": session_id}
            )
        except Exception as e:
            logging.error(f"Error in stream_stop: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/transcribe", methods=["POST"])
    def transcribe_audio():
        try:
            if "audio" not in request.files:
                return jsonify({"error": "No audio file provided"}), 400

            audio_file = request.files["audio"]
            audio_data = audio_file.read()

            transcript = speech_service.transcribe_audio_stream(audio_data)

            if transcript:
                return jsonify({"success": True, "transcript": transcript})
            else:
                return jsonify({"success": False, "error": "Could not transcribe audio"}), 500
        except Exception as e:
            logging.error(f"Error in transcribe_audio: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/synthesize", methods=["POST"])
    def synthesize_speech():
        try:
            data = request.get_json()
            text = data.get("text", "")
            if not text:
                return jsonify({"error": "No text provided"}), 400

            audio_data = speech_service.text_to_speech(text)
            if audio_data:
                return send_file(io.BytesIO(audio_data), mimetype="audio/mpeg", as_attachment=False)
            else:
                return jsonify({"error": "Could not synthesize speech"}), 500
        except Exception as e:
            logging.error(f"Error in synthesize_speech: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/converse", methods=["POST"])
    def converse():
        try:
            data = request.get_json()
            user_message = data.get("message", "")
            session_id = data.get("session_id", "default")
            if not user_message:
                return jsonify({"error": "No message provided"}), 400

            if session_id not in conversation_sessions:
                conversation_sessions[session_id] = []
            conversation_history = conversation_sessions[session_id]

            intent_result = intent_service.classify_intent(user_message)
            bot_response = intent_service.generate_response(
                user_message, intent_result["intent"], conversation_history
            )

            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": bot_response})

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
            logging.error(f"Error in converse: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/clear-session", methods=["POST"])
    def clear_session():
        try:
            data = request.get_json()
            session_id = data.get("session_id", "default")
            if session_id in conversation_sessions:
                del conversation_sessions[session_id]
            return jsonify({"success": True, "message": "Session cleared"})
        except Exception as e:
            logging.error(f"Error in clear_session: {e}")
            return jsonify({"error": str(e)}), 500

    # Log configuration status
    if config.is_configured():
        logging.info("✅ Configuration loaded successfully")
    else:
        logging.warning("⚠️  Configuration incomplete - some features may not work")

    return app


def main():
    """Main entry point for the application."""
    app = create_app()

    try:
        logging.info("🚀 Starting Flask development server...")
        app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5002)
    except Exception as e:
        logging.error(f"❌ Failed to start server: {e}")
        raise


if __name__ == "__main__":
    main()
