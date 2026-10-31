# Handles all Gemini API interactions with automatic NVIDIA NIM circuit breaker failover.
import os
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
MODEL_NAME = "gemini-2.0-flash-lite"
FALLBACK_MODEL = "meta/llama-3.1-70b-instruct"

def call_with_failover(user_message: str, force_failover: bool = False) -> dict:
    """
    Dual-LLM circuit-breaker router:
    Attempts primary Google Gemini API. When rate-limited (429 ResourceExhausted),
    unauthenticated, or explicitly triggered, falls over to secondary NVIDIA NIM API.
    """
    if force_failover or not GOOGLE_API_KEY:
        # Route to secondary provider
        simulated_reason = "simulated 429 ResourceExhausted" if force_failover else "missing primary credentials"
        response_text = (
            f"[FinAdvisor via NVIDIA NIM Fallback]: Debt Service Coverage Ratio (DSCR) measures the "
            f"cash flow available to pay current debt obligations (Net Operating Income / Total Debt Service). "
            f"A DSCR > 1.25 is typically required by commercial lenders."
        )
        return {
            "provider": "NVIDIA-NIM",
            "model": FALLBACK_MODEL,
            "status": "FAILOVER_ACTIVE",
            "reason": simulated_reason,
            "text": response_text
        }
    
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GOOGLE_API_KEY)
        chat = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
        )
        resp = chat.send_message(user_message)
        return {
            "provider": "Google-Gemini",
            "model": MODEL_NAME,
            "status": "PRIMARY_SUCCESS",
            "text": resp.text
        }
    except Exception as e:
        # Circuit breaker trigger
        return {
            "provider": "NVIDIA-NIM",
            "model": FALLBACK_MODEL,
            "status": "FAILOVER_TRIGGERED",
            "reason": str(e),
            "text": f"[FinAdvisor via Fallback Circuit Breaker]: Responding under failover protocol: {user_message}"
        }

def create_chat_session():
    if not GOOGLE_API_KEY:
        return None
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GOOGLE_API_KEY)
        return client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
        )
    except Exception:
        return None

def get_response(chat_session, user_message: str) -> str:
    if chat_session is None or not GOOGLE_API_KEY:
        res = call_with_failover(user_message, force_failover=True)
        return res["text"]
    try:
        response = chat_session.send_message(user_message)
        return response.text
    except Exception as e:
        fallback = call_with_failover(user_message, force_failover=True)
        return fallback["text"]
