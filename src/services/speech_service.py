"""
Speech service for handling speech-to-text and text-to-speech operations.
"""

import logging
import requests
from typing import Optional
from azure.cognitiveservices.speech import SpeechConfig, SpeechRecognizer, AudioConfig
from azure.cognitiveservices.speech.audio import PushAudioInputStream

logger = logging.getLogger(__name__)


class SpeechService:
    """Service for handling Azure Speech Services and ElevenLabs."""

    def __init__(self, config):
        """Initialize the speech service."""
        self.config = config
        self.azure_speech_config = config.get_azure_speech_config()
        self.elevenlabs_api_key = config.ELEVENLABS_API_KEY

        # Initialize Azure Speech Service
        if self.azure_speech_config["api_key"] and self.azure_speech_config["region"]:
            self.speech_config = SpeechConfig(
                subscription=self.azure_speech_config["api_key"],
                region=self.azure_speech_config["region"],
            )
            logger.info("✅ Azure Speech Services initialized")
        else:
            logger.warning("⚠️ Azure Speech Services not configured")
            self.speech_config = None

    def create_streaming_recognizer(
        self, audio_stream: PushAudioInputStream
    ) -> Optional[SpeechRecognizer]:
        """Create a streaming speech recognizer."""
        if not self.speech_config:
            logger.error("Azure Speech Services not configured")
            return None

        try:
            audio_config = AudioConfig(stream=audio_stream)
            recognizer = SpeechRecognizer(
                speech_config=self.speech_config, audio_config=audio_config
            )
            logger.info("Streaming speech recognizer created")
            return recognizer
        except Exception as e:
            logger.error(f"Error creating recognizer: {e}")
            return None

    def text_to_speech(
        self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    ) -> Optional[bytes]:
        """Convert text to speech using ElevenLabs."""
        if not self.elevenlabs_api_key:
            logger.error("ElevenLabs API key not configured")
            return None

        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

            headers = {"xi-api-key": self.elevenlabs_api_key}

            data = {
                "text": text,
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
            }

            response = requests.post(url, json=data, headers=headers, timeout=30)

            if response.status_code == 200:
                logger.info("Text-to-speech conversion successful")
                return response.content
            else:
                logger.error(
                    f"ElevenLabs API error: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {e}")
            return None

    def transcribe_audio_stream(
        self, audio_data: bytes, save_path: Optional[str] = None
    ) -> Optional[str]:
        """Transcribe audio data using Azure Speech Services.
        If save_path is provided, write the WAV bytes there for debugging; otherwise use a temp file.
        """
        if not self.speech_config:
            logger.error("Azure Speech Services not configured")
            return None

        import tempfile
        import os

        file_path = save_path
        cleanup = False
        try:
            if not file_path:
                # Use temporary file if no save_path provided
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".wav"
                ) as tmp_file:
                    tmp_file.write(audio_data)
                    file_path = tmp_file.name
                cleanup = True
            else:
                # Persist to the provided path for debugging
                with open(file_path, "wb") as f:
                    f.write(audio_data)

            from azure.cognitiveservices.speech.audio import AudioConfig

            audio_config = AudioConfig(filename=file_path)
            recognizer = SpeechRecognizer(
                speech_config=self.speech_config, audio_config=audio_config
            )

            result = recognizer.recognize_once()

            if result.reason.name == "ResultReason.RecognizedSpeech":
                logger.info(f"Recognized: {result.text}")
                return result.text
            elif result.reason.name == "ResultReason.NoMatch":
                logger.warning("No speech could be recognized")
                return None
            else:
                logger.warning(f"Recognition failed: {result.reason}")
                return None
        except Exception as e:
            logger.error(f"Error in transcription: {e}")
            return None
        finally:
            if cleanup and file_path and os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except:
                    pass
