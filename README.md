# Conversational IVR System

A voice-enabled Interactive Voice Response (IVR) system with Azure Speech Services and ElevenLabs.

## Features

- **Live Speech-to-Text**: Real-time speech transcription using Azure Speech Services
- **Intent Classification**: AI-powered intent detection (question, complaint, or other)
- **Natural Responses**: Context-aware conversational responses using Azure OpenAI
- **Text-to-Speech**: Natural voice synthesis using ElevenLabs
- **Web Interface**: Browser-based interface matching Emblematic branding
- **Conversation History**: Maintains context across multiple turns

## Architecture

The system uses a modular architecture with the following components:

### Services

- **SpeechService**: Handles speech-to-text (Azure) and text-to-speech (ElevenLabs)
- **IntentService**: Classifies user intent and generates appropriate responses using Azure OpenAI

### Intent Classification

The system automatically classifies user input into three categories:
- **Question**: User is asking for information or clarification
- **Complaint**: User is expressing dissatisfaction or reporting an issue
- **Other**: General conversation, greeting, or non-specific intent

Based on the classified intent, the system generates contextually appropriate responses:
- Questions receive informative, helpful responses
- Complaints receive empathetic, problem-solving responses
- Other interactions receive friendly, conversational responses

## Installation

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   cd conversational-ivr
   pip install -r requirements.txt
   ```

3. **Configure API keys**:
   - Copy `keys_example.py` to `keys.py`
   - Add your API keys to `keys.py`:
     - Azure Speech Services (Key and Region)
     - ElevenLabs API Key
     - Azure OpenAI (Key, Endpoint, and Version)

## Running the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5002`

## Usage

1. Click "Start Recording" to begin
2. Speak your message when prompted
3. Click "Stop Recording" to process your audio
4. The system will:
   - Transcribe your speech to text
   - Classify your intent
   - Generate an appropriate response
   - Play the response back to you using ElevenLabs voice synthesis

## API Endpoints

- `POST /api/transcribe`: Transcribe audio to text
- `POST /api/synthesize`: Convert text to speech
- `POST /api/converse`: Handle conversational turn with intent classification
- `POST /api/clear-session`: Clear conversation history

## Configuration

The following services must be configured:

### Azure Speech Services
Required for speech-to-text transcription.

### ElevenLabs
Required for natural-sounding text-to-speech.

### Azure OpenAI
Required for intent classification and response generation.

## Notes

- The microphone permission will be requested by your browser
- Recording quality depends on your microphone and environment
- The system maintains conversation context across turns
- Each session has a unique ID for conversation management

## How it works
- Click Start Recording and speak
- Click Stop Recording; the browser converts WebM to WAV
- Azure Speech transcribes to text
- The system classifies intent (question/complaint/other)
- Azure OpenAI generates a contextual response
- ElevenLabs synthesizes and plays audio
- The UI shows the conversation and intent analysis
- The system maintains context across turns and adapts responses by intent.
- See SETUP_GUIDE.md for details on API setup and troubleshooting.