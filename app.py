"""
Conversational IVR - Main Flask Application
A voice-enabled IVR system with Azure Speech Services and ElevenLabs.
"""

from flask import Flask
from flask_cors import CORS
import logging
from src.config.config import config
from src.services.speech_service import SpeechService
from src.services.intent_service import IntentService
from src.routes.routes import Routes


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

    # Register routes
    Routes(app, config, speech_service, intent_service)

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
