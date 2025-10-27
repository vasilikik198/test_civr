"""
Utility functions for the Conversational IVR application.
"""

import os
import io
import subprocess
import logging

logger = logging.getLogger(__name__)


def convert_webm_to_wav(webm_data: bytes, output_path: str = None) -> bytes:
    """Convert WebM audio data to WAV format using ffmpeg."""
    try:
        # Check if ffmpeg is available
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(
                "ffmpeg not found. Please install ffmpeg for audio conversion."
            )
            return None

        # Use a temporary output path if not provided
        if output_path is None:
            import tempfile

            _, output_path = tempfile.mkstemp(suffix=".wav")
            should_delete = True
        else:
            should_delete = False

        try:
            # Run ffmpeg to convert WebM to WAV
            process = subprocess.Popen(
                [
                    "ffmpeg",
                    "-i",
                    "pipe:0",  # Input from stdin
                    "-f",
                    "wav",  # Output format
                    "-acodec",
                    "pcm_s16le",  # PCM 16-bit little-endian
                    "-ar",
                    "16000",  # Sample rate
                    "-ac",
                    "1",  # Mono channel
                    output_path,
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout, stderr = process.communicate(input=webm_data)

            if process.returncode != 0:
                logger.error(f"ffmpeg conversion failed: {stderr.decode()}")
                return None

            # Read the converted file
            with open(output_path, "rb") as f:
                wav_data = f.read()

            return wav_data

        finally:
            if should_delete and os.path.exists(output_path):
                os.unlink(output_path)

    except FileNotFoundError:
        logger.error("ffmpeg not installed. Please install ffmpeg.")
        return None
    except Exception as e:
        logger.error(f"Error converting WebM to WAV: {e}")
        return None


def ensure_wav_format(audio_data: bytes, format: str = "webm") -> bytes:
    """Ensure audio is in WAV format for Azure Speech Services."""
    if format.lower() == "wav":
        return audio_data

    # Try to convert WebM to WAV
    if format.lower() in ["webm", "ogg"]:
        wav_data = convert_webm_to_wav(audio_data)
        if wav_data:
            return wav_data
        else:
            logger.warning("Could not convert audio format. Using original data.")
            return audio_data

    return audio_data
