"""
Gemini API client – handles all communication with Google GenAI.

Responsibilities:
  • Configure the SDK once
  • Send chat requests with retry + exponential back-off
  • Parse and return the response text
  • Log every API call (latency, tokens, errors)
"""

from __future__ import annotations

import time
from typing import Any

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class GeminiClient:
    """Thin wrapper around the Google GenAI SDK."""

    def __init__(self) -> None:
        settings.validate()
        genai.configure(api_key=settings.GEMINI_API_KEY)

        self._generation_config = genai.types.GenerationConfig(
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_OUTPUT_TOKENS,
            top_p=settings.TOP_P,
            top_k=settings.TOP_K,
        )

        self._model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=self._generation_config,
        )

        logger.info(
            "GeminiClient initialised  model=%s  temp=%.2f  max_tokens=%d",
            settings.GEMINI_MODEL,
            settings.TEMPERATURE,
            settings.MAX_OUTPUT_TOKENS,
        )

    # ── public API ──────────────────────────────────────────────
    def send_message(
        self,
        message: str,
        history: list[dict[str, str]],
        system_instruction: str = "",
    ) -> str:
        """
        Send a message with conversation history and return the reply.

        Parameters
        ----------
        message : str
            The latest user message.
        history : list[dict]
            Previous turns as ``[{"role": "user"|"model", "parts": [text]}]``.
        system_instruction : str
            System-level instruction prepended to the conversation.

        Returns
        -------
        str
            The model's reply text.
        """
        # Build a model instance with system instruction for this call
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=self._generation_config,
            system_instruction=system_instruction or None,
        )

        chat = model.start_chat(history=history)

        return self._call_with_retry(chat, message)

    # ── internals ───────────────────────────────────────────────
    def _call_with_retry(self, chat: Any, message: str) -> str:
        """Retry with exponential back-off on transient failures."""
        last_error: Exception | None = None

        for attempt in range(1, settings.MAX_RETRIES + 1):
            try:
                t0 = time.perf_counter()
                response = chat.send_message(message)
                elapsed = time.perf_counter() - t0

                text = response.text.strip()

                # Log success
                logger.info(
                    "Gemini OK  attempt=%d  latency=%.2fs  reply_chars=%d",
                    attempt,
                    elapsed,
                    len(text),
                )
                return text

            except (
                google_exceptions.ResourceExhausted,
                google_exceptions.ServiceUnavailable,
                google_exceptions.DeadlineExceeded,
                google_exceptions.InternalServerError,
            ) as exc:
                last_error = exc
                wait = settings.RETRY_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "Gemini transient error  attempt=%d/%d  wait=%.1fs  error=%s",
                    attempt,
                    settings.MAX_RETRIES,
                    wait,
                    exc,
                )
                time.sleep(wait)

            except google_exceptions.InvalidArgument as exc:
                logger.error("Gemini invalid request: %s", exc)
                raise

            except Exception as exc:  # noqa: BLE001
                logger.error("Gemini unexpected error: %s", exc, exc_info=True)
                raise

        # All retries exhausted
        logger.error("Gemini request failed after %d retries", settings.MAX_RETRIES)
        raise RuntimeError(
            f"Gemini API call failed after {settings.MAX_RETRIES} retries: {last_error}"
        )
