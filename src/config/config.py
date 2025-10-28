"""
Configuration module for Conversational IVR.
Handles all configuration settings, API keys, and environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class."""

    # Flask Configuration
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    STREAM_UPLOADS_DIR = os.environ.get("STREAM_UPLOADS_DIR", "stream_uploads")

    # Azure Speech Configuration
    AZURE_SPEECH_KEY = None
    AZURE_SPEECH_REGION = None

    # ElevenLabs Configuration
    ELEVENLABS_API_KEY = None

    # OpenAI Configuration (for intent classification)
    AZURE_OPENAI_API_KEY = None
    AZURE_OPENAI_ENDPOINT = None
    AZURE_OPENAI_API_VERSION = None

    def __init__(self):
        """Initialize configuration by loading API keys."""
        self._load_api_keys()
        self._validate_config()
        # Ensure stream uploads directory exists
        try:
            os.makedirs(self.STREAM_UPLOADS_DIR, exist_ok=True)
        except Exception:
            pass

    def _load_api_keys(self):
        """Load API keys from keys.py or environment variables."""
        try:
            from keys import (
                AZURE_SPEECH_KEY,
                AZURE_SPEECH_REGION,
                ELEVENLABS_API_KEY,
                AZURE_OPENAI_API_KEY,
                AZURE_OPENAI_ENDPOINT,
                AZURE_OPENAI_API_VERSION,
            )

            self.AZURE_SPEECH_KEY = AZURE_SPEECH_KEY
            self.AZURE_SPEECH_REGION = AZURE_SPEECH_REGION
            self.ELEVENLABS_API_KEY = ELEVENLABS_API_KEY
            self.AZURE_OPENAI_API_KEY = AZURE_OPENAI_API_KEY
            self.AZURE_OPENAI_ENDPOINT = AZURE_OPENAI_ENDPOINT
            self.AZURE_OPENAI_API_VERSION = AZURE_OPENAI_API_VERSION
        except ImportError:
            # Fallback to environment variables
            self.AZURE_SPEECH_KEY = os.environ.get("AZURE_SPEECH_KEY")
            self.AZURE_SPEECH_REGION = os.environ.get("AZURE_SPEECH_REGION")
            self.ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
            self.AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
            self.AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
            self.AZURE_OPENAI_API_VERSION = os.environ.get(
                "AZURE_OPENAI_API_VERSION", "2024-12-01-preview"
            )

    def _validate_config(self):
        """Validate configuration and show warnings if needed."""
        missing_configs = []

        if not self.AZURE_SPEECH_KEY or not self.AZURE_SPEECH_REGION:
            missing_configs.append("Azure Speech Services")

        if not self.ELEVENLABS_API_KEY:
            missing_configs.append("ElevenLabs")

        if not self.AZURE_OPENAI_API_KEY or not self.AZURE_OPENAI_ENDPOINT:
            missing_configs.append("Azure OpenAI")

        if missing_configs:
            print(f"Warning: Missing configuration for: {', '.join(missing_configs)}")

    def get_azure_speech_config(self):
        """Get Azure Speech configuration as a dictionary."""
        return {"api_key": self.AZURE_SPEECH_KEY, "region": self.AZURE_SPEECH_REGION}

    def get_openai_config(self):
        """Get OpenAI configuration as a dictionary."""
        return {
            "api_key": self.AZURE_OPENAI_API_KEY,
            "azure_endpoint": self.AZURE_OPENAI_ENDPOINT,
            "api_version": self.AZURE_OPENAI_API_VERSION,
        }

    def is_configured(self):
        """Check if required services are configured."""
        return bool(
            self.AZURE_SPEECH_KEY
            and self.AZURE_SPEECH_REGION
            and self.ELEVENLABS_API_KEY
            and self.AZURE_OPENAI_API_KEY
            and self.AZURE_OPENAI_ENDPOINT
        )


# Global configuration instance
config = Config()
