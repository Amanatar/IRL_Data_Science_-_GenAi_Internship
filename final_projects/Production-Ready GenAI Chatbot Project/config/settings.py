"""
Application configuration – loads from environment / .env file.

All secrets and tunables live here so nothing is hardcoded elsewhere.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()  # reads .env at project root


@dataclass(frozen=True)
class Settings:
    """Immutable application settings."""

    # ── Gemini API ──────────────────────────────────────────────
    GEMINI_API_KEY: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "")
    )
    GEMINI_MODEL: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    )

    # ── NVIDIA API ──────────────────────────────────────────────
    NVIDIA_API_KEY: str = field(
        default_factory=lambda: os.getenv("NVIDIA_API_KEY", "")
    )
    NVIDIA_MODEL: str = field(
        default_factory=lambda: os.getenv("NVIDIA_MODEL", "moonshotai/kimi-k2-thinking")
    )

    # ── Generation hyper-params ─────────────────────────────────
    TEMPERATURE: float = field(
        default_factory=lambda: float(os.getenv("TEMPERATURE", "0.7"))
    )
    MAX_OUTPUT_TOKENS: int = field(
        default_factory=lambda: int(os.getenv("MAX_OUTPUT_TOKENS", "2048"))
    )
    TOP_P: float = field(
        default_factory=lambda: float(os.getenv("TOP_P", "0.9"))
    )
    TOP_K: int = field(
        default_factory=lambda: int(os.getenv("TOP_K", "40"))
    )

    # ── Memory / context ────────────────────────────────────────
    MAX_HISTORY_TURNS: int = field(
        default_factory=lambda: int(os.getenv("MAX_HISTORY_TURNS", "20"))
    )

    # ── Retry ───────────────────────────────────────────────────
    MAX_RETRIES: int = field(
        default_factory=lambda: int(os.getenv("MAX_RETRIES", "3"))
    )
    RETRY_DELAY: float = field(
        default_factory=lambda: float(os.getenv("RETRY_DELAY", "1.0"))
    )

    # ── App meta ────────────────────────────────────────────────
    APP_TITLE: str = "💰 FinWise — AI Financial Advisor"
    APP_ICON: str = "💰"
    DISCLAIMER: str = (
        "⚠️ **Disclaimer:** This chatbot provides educational financial "
        "guidance only and not professional financial advice. Always consult "
        "a certified financial planner before making investment decisions."
    )

    def validate(self) -> None:
        """Raise early if critical config is missing."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.GEMINI_API_KEY and not self.NVIDIA_API_KEY:
            raise EnvironmentError(
                "Neither GEMINI_API_KEY nor NVIDIA_API_KEY is set. "
                "Please configure at least one API key in your .env file."
            )
        if not self.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. Chatbot will rely exclusively on NVIDIA failover.")
        if not self.NVIDIA_API_KEY:
            logger.warning("NVIDIA_API_KEY is not set. Chatbot has no fallback protection if Gemini fails.")


# Singleton ─ import `settings` everywhere
settings = Settings()
