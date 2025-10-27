"""
Intent service for classifying user messages and generating appropriate responses.
"""

import logging
from typing import Dict, Any
import openai

logger = logging.getLogger(__name__)


class IntentService:
    """Service for intent classification and conversation management."""

    def __init__(self, config):
        """Initialize the intent service."""
        self.config = config
        openai_config = config.get_openai_config()

        if openai_config["api_key"] and openai_config["azure_endpoint"]:
            # Initialize Azure OpenAI client
            self.client = openai.AzureOpenAI(
                api_key=openai_config["api_key"],
                api_version=openai_config["api_version"],
                azure_endpoint=openai_config["azure_endpoint"],
            )
            logger.info("✅ Intent Service initialized with Azure OpenAI")
        else:
            logger.warning("⚠️ OpenAI not configured")
            self.client = None

    def classify_intent(self, user_message: str) -> Dict[str, Any]:
        """Classify user intent: question, complaint, or other."""
        if not self.client:
            return {
                "intent": "other",
                "confidence": 0.0,
                "reasoning": "OpenAI not configured",
            }

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an intent classifier. Classify user messages into one of these categories:
                        - question: User is asking for information or clarification
                        - complaint: User is expressing dissatisfaction or reporting an issue
                        - other: General conversation, greeting, or non-specific intent
                        
                        Respond ONLY with a JSON object containing:
                        {
                            "intent": "question|complaint|other",
                            "confidence": <float between 0 and 1>,
                            "reasoning": "brief explanation"
                        }""",
                    },
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            result = eval(response.choices[0].message.content)
            logger.info(
                f"Intent classified: {result['intent']} (confidence: {result['confidence']})"
            )
            return result

        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return {
                "intent": "other",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
            }

    def generate_response(
        self, user_message: str, intent: str, conversation_history: list
    ) -> str:
        """Generate an appropriate response based on intent and conversation history."""
        if not self.client:
            return (
                "I'm sorry, but I'm having trouble processing your request right now."
            )

        # Define system prompts based on intent
        system_prompts = {
            "question": """You are a helpful virtual assistant. The user has asked a question.
            Provide a clear, concise, and helpful response. If you need more context, ask a follow-up question.
            Be conversational and natural in your response.""",
            "complaint": """You are an empathetic customer service assistant. The user has raised a complaint or concern.
            Acknowledge their concern, show empathy, and offer to help resolve the issue.
            Be warm, understanding, and professional in your response.""",
            "other": """You are a friendly and professional virtual assistant.
            Engage naturally with the user. Keep responses brief and conversational.
            If appropriate, you can ask how you can help them today.""",
        }

        system_prompt = system_prompts.get(intent, system_prompts["other"])

        # Build conversation messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history (limit to last 6 messages to keep context manageable)
        for msg in conversation_history[-6:]:
            messages.append(msg)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4", messages=messages, temperature=0.7, max_tokens=150
            )

            bot_response = response.choices[0].message.content.strip()
            logger.info(
                f"Generated response for intent '{intent}': {bot_response[:100]}..."
            )
            return bot_response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble understanding. Could you please rephrase that?"
