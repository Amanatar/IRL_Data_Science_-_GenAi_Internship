# chatbot_engine.py — The Logic
# Handles all Gemini API interactions. Swap this file to switch to a different LLM.

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

# --- Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.0-flash-lite"

if not GOOGLE_API_KEY:
    raise EnvironmentError(
        "GOOGLE_API_KEY not found. Please set it in your .env file."
    )

# Initialise the Gemini client
_client = genai.Client(api_key=GOOGLE_API_KEY)


def create_chat_session():
    """
    Initialise a new Gemini chat session with the system prompt injected as
    a system instruction. The SDK automatically maintains conversation history.

    Returns:
        google.genai.chats.Chat
    """
    return _client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        ),
    )


def get_response(chat_session, user_message: str) -> str:
    """
    Send a message to the Gemini model and return the text response.

    Args:
        chat_session: An active google.genai Chat object.
        user_message:  The user's input string.

    Returns:
        The model's response as a plain string.
    """
    try:
        response = chat_session.send_message(user_message)
        return response.text
    except Exception as e:
        return f"⚠️ An error occurred: {str(e)}"
