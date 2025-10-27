# Conversational IVR - Setup Guide

This guide will help you set up and run the Conversational IVR system.

## Prerequisites

Before you begin, ensure you have:

1. Python 3.8 or higher installed
2. Access to the following services:
   - Azure Speech Services (for speech-to-text)
   - ElevenLabs API (for text-to-speech)
   - Azure OpenAI (for intent classification and responses)

## Installation Steps

### 1. Create Virtual Environment

```bash
cd conversational-ivr
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Open `keys.py` and add your API keys:

```python
# Azure Speech Services
AZURE_SPEECH_KEY = "your_actual_azure_speech_key"
AZURE_SPEECH_REGION = "eastus"  # or your region

# ElevenLabs
ELEVENLABS_API_KEY = "your_actual_elevenlabs_key"

# Azure OpenAI
AZURE_OPENAI_API_KEY = "your_actual_openai_key"
AZURE_OPENAI_ENDPOINT = "https://your-resource.cognitiveservices.azure.com"
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
```

### 4. Get API Keys

#### Azure Speech Services
1. Go to [Azure Portal](https://portal.azure.com)
2. Create a Speech Services resource
3. Copy the API key and region

#### ElevenLabs
1. Go to [ElevenLabs](https://elevenlabs.io)
2. Sign up for an account
3. Get your API key from the dashboard
4. Note: The default voice ID is already configured, but you can change it in `src/services/speech_service.py`

#### Azure OpenAI
1. Go to [Azure Portal](https://portal.azure.com)
2. Create an Azure OpenAI resource
3. Copy the endpoint and API key
4. Deploy a GPT-4 model

## Running the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5002`

## Usage

1. Open your browser and navigate to `http://127.0.0.1:5002`
2. Click "Start Recording"
3. Allow microphone access when prompted
4. Speak your message
5. Click "Stop Recording"
6. The system will:
   - Transcribe your speech
   - Classify your intent (question, complaint, or other)
   - Generate an appropriate response
   - Play the response back using ElevenLabs voice

## Features

### Intent Classification
The system automatically classifies user input into:
- **Question**: User is asking for information
- **Complaint**: User is expressing dissatisfaction
- **Other**: General conversation or greeting

### Conversational Flow
- Each session maintains conversation history
- Context-aware responses based on intent
- Natural conversation flow

### Voice Synthesis
- Uses ElevenLabs for natural-sounding voices
- Default voice: "21m00Tcm4TlvDq8ikWAM"
- Customizable voices available

## Troubleshooting

### Microphone Issues
- Ensure your browser has microphone permissions
- Try refreshing the page if microphone access is denied

### Azure Speech Services Errors
- Verify your API key and region are correct
- Check that your Azure Speech Services resource is active
- Ensure the audio format is WAV (automatically converted in browser)

### ElevenLabs Errors
- Verify your API key is correct
- Check your ElevenLabs account has available credits
- Default voice ID may need to be updated if voice not found

### Azure OpenAI Errors
- Verify your API key and endpoint are correct
- Ensure you have a GPT-4 model deployed
- Check model availability in your region

## Project Structure

```
conversational-ivr/
├── app.py                 # Main Flask application
├── keys.py                # API keys (not in version control)
├── requirements.txt       # Python dependencies
├── src/
│   ├── config/           # Configuration
│   ├── services/          # Business logic
│   │   ├── speech_service.py    # Azure Speech & ElevenLabs
│   │   └── intent_service.py    # Intent classification
│   └── routes/            # Flask routes
└── templates/             # HTML templates
```

## Next Steps

- Customize voice settings in `src/services/speech_service.py`
- Modify intent classification prompts in `src/services/intent_service.py`
- Add more sophisticated conversation handling
- Integrate with external data sources or APIs

## Notes

- This is a demo application and not production-ready
- Conversation history is stored in memory (lost on server restart)
- For production, consider:
  - Persistent storage for conversations
  - User authentication
  - Rate limiting
  - Error logging and monitoring
  - Proper security measures

