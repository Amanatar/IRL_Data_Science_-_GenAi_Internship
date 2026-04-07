"""
Session memory manager.

Handles:
  • Chat history (list of turns) with configurable window
  • User profile extraction & storage (income, goals, risk level …)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class UserProfile:
    """Financial profile collected during conversation."""

    income: str = ""
    goals: str = ""
    risk_level: str = ""       # low / medium / high
    age: str = ""
    dependents: str = ""
    existing_investments: str = ""

    def to_dict(self) -> dict[str, str]:
        return {k: v for k, v in self.__dict__.items() if v}

    def is_empty(self) -> bool:
        return not any(self.__dict__.values())


@dataclass
class MemoryManager:
    """Per-session conversation memory."""

    history: list[dict] = field(default_factory=list)
    profile: UserProfile = field(default_factory=UserProfile)

    # ── history management ──────────────────────────────────────
    def add_user_message(self, text: str) -> None:
        """Append a user turn and attempt profile extraction."""
        self.history.append({"role": "user", "parts": [text]})
        self._extract_profile(text)
        self._trim_history()

    def add_model_message(self, text: str) -> None:
        """Append a model turn."""
        self.history.append({"role": "model", "parts": [text]})
        self._trim_history()

    def get_history(self) -> list[dict]:
        """Return the current (trimmed) history."""
        return list(self.history)

    def clear(self) -> None:
        """Reset everything."""
        self.history.clear()
        self.profile = UserProfile()
        logger.info("Memory cleared")

    # ── profile extraction (heuristic) ──────────────────────────
    def _extract_profile(self, text: str) -> None:
        """Best-effort extraction of financial profile from user message."""
        lower = text.lower()

        # Income patterns
        income_match = re.search(
            r"(?:income|salary|earn|make|take.?home)\s*(?:is|of|around|about|:)?\s*"
            r"(?:₹|rs\.?|inr|usd|\$)?\s*([\d,]+(?:\.\d+)?)\s*(?:k|lakh|lac|lpa|per\s*month|pm|p\.m\.)?",
            lower,
        )
        if income_match and not self.profile.income:
            self.profile.income = income_match.group(0).strip()
            logger.debug("Extracted income: %s", self.profile.income)

        # Risk level
        for level in ("conservative", "low risk", "low-risk"):
            if level in lower and not self.profile.risk_level:
                self.profile.risk_level = "low"
        for level in ("moderate", "medium risk", "medium-risk", "balanced"):
            if level in lower and not self.profile.risk_level:
                self.profile.risk_level = "medium"
        for level in ("aggressive", "high risk", "high-risk"):
            if level in lower and not self.profile.risk_level:
                self.profile.risk_level = "high"

        # Age
        age_match = re.search(r"\b(\d{2})\s*(?:years?\s*old|yrs?|yo)\b", lower)
        if age_match and not self.profile.age:
            self.profile.age = age_match.group(1)
            logger.debug("Extracted age: %s", self.profile.age)

    # ── trim to window ──────────────────────────────────────────
    def _trim_history(self) -> None:
        """Keep only the last N turns (pair of user + model = 2 entries)."""
        max_entries = settings.MAX_HISTORY_TURNS * 2
        if len(self.history) > max_entries:
            self.history = self.history[-max_entries:]
            logger.debug("History trimmed to %d entries", len(self.history))
