"""
NVIDIA API client – acts as the secondary/fallback provider.
Uses the OpenAI Python SDK pointing to integrate.api.nvidia.com.

Responsibilities:
  • Connect to NVIDIA API
  • Send chat requests containing history
  • Retrieve thinking/reasoning and final response
  • Log execution
"""

from __future__ import annotations

import time
from typing import Any

from openai import OpenAI, APIError
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class NvidiaClient:
    """Wrapper around the NVIDIA OpenAI-compatible API."""

    def __init__(self) -> None:
        settings.validate()
        
        # Don't fail instantiation if only the key is missing but the other exists
        if not settings.NVIDIA_API_KEY:
            logger.warning("NvidiaClient initialized without an API key.")

        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=settings.NVIDIA_API_KEY
        )
        
        logger.info(
            "NvidiaClient initialised  model=%s  temp=%.2f  max_tokens=%d",
            settings.NVIDIA_MODEL,
            settings.TEMPERATURE,
            settings.MAX_OUTPUT_TOKENS,
        )

    # ── public API ──────────────────────────────────────────────
    def send_message(
        self,
        message: str,
        history: list[dict[str, Any]],
        system_instruction: str = "",
    ) -> str:
        """
        Send a message using the OpenAI schema {"role": "...", "content": "..."}.
        
        Note: The incoming 'history' from MemoryManager currently uses Gemini format
        {"role": "user"|"model", "parts": ["text"]}. We will convert it here.
        """
        
        messages = []
        
        # 1. System Prompt
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
            
        # 2. History (converting from Gemini array to OpenAI array)
        for turn in history:
            role = turn.get("role", "user")
            # Map "model" to "assistant"
            role = "assistant" if role == "model" else role
            
            # Extract content
            parts = turn.get("parts", [])
            content = parts[0] if parts else ""
            
            messages.append({"role": role, "content": content})
            
        # 3. Current User Message
        messages.append({"role": "user", "content": message})
        
        return self._call_with_retry(messages)

    # ── internals ───────────────────────────────────────────────
    def _call_with_retry(self, messages: list[dict]) -> str:
        """Retry with exponential back-off on transient failures."""
        if not settings.NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY is missing. Cannot perform request.")

        last_error: Exception | None = None

        for attempt in range(1, settings.MAX_RETRIES + 1):
            try:
                t0 = time.perf_counter()
                
                completion = self.client.chat.completions.create(
                    model=settings.NVIDIA_MODEL,
                    messages=messages,
                    temperature=settings.TEMPERATURE,
                    top_p=settings.TOP_P,
                    max_tokens=settings.MAX_OUTPUT_TOKENS,
                )
                
                elapsed = time.perf_counter() - t0
                
                choice = completion.choices[0]
                
                # Safely check for message or delta depending on streaming vs non-streaming
                message_obj = getattr(choice, "message", None)
                delta_obj = getattr(choice, "delta", None)
                
                reasoning_from_message = getattr(message_obj, "reasoning_content", None) if message_obj else None
                reasoning_from_delta = getattr(delta_obj, "reasoning_content", None) if delta_obj else None
                
                reasoning = reasoning_from_delta or reasoning_from_message
                content = (message_obj.content if message_obj else getattr(delta_obj, "content", "")) or ""
                
                text = content.strip()
                
                msg_len = len(text)
                if reasoning:
                    logger.debug("NVIDIA reasoning included %d characters", len(reasoning.strip()))
                
                logger.info(
                    "NVIDIA OK  attempt=%d  latency=%.2fs  reply_chars=%d",
                    attempt,
                    elapsed,
                    msg_len,
                )
                return text

            except APIError as exc:
                last_error = exc
                wait = settings.RETRY_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "NVIDIA API transient error  attempt=%d/%d  wait=%.1fs  error=%s",
                    attempt,
                    settings.MAX_RETRIES,
                    wait,
                    exc,
                )
                time.sleep(wait)

            except Exception as exc:  # noqa: BLE001
                logger.error("NVIDIA unexpected error: %s", exc, exc_info=True)
                raise exc

        # All retries exhausted
        logger.error("NVIDIA request failed after %d retries", settings.MAX_RETRIES)
        raise RuntimeError(
            f"NVIDIA API call failed after {settings.MAX_RETRIES} retries: {last_error}"
        )
