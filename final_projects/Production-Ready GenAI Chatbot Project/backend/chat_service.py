"""
Chat service — the core orchestrator.

Wires together:
  • MemoryManager  (session state)
  • GeminiClient   (LLM calls)
  • SystemPrompt   (persona / guardrails)
  • Financial tools (risk profiler, SIP calculator)
"""

from __future__ import annotations

from backend.gemini_client import GeminiClient
from backend.nvidia_client import NvidiaClient
from backend.memory_manager import MemoryManager
from prompts.system_prompt import build_system_prompt
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Fallback when Gemini is unreachable ─────────────────────────
FALLBACK_RESPONSE = (
    "I'm sorry — I'm having trouble connecting to my knowledge engine right now. "
    "Please try again in a moment. In the meantime, here are some general tips:\n\n"
    "• **Build an emergency fund** covering 3-6 months of expenses.\n"
    "• **Follow the 50/30/20 rule** — 50 % needs, 30 % wants, 20 % savings.\n"
    "• **Start a SIP** in an index fund for disciplined, long-term investing.\n\n"
    "📌 _This is educational guidance only — not professional financial advice._"
)


class ChatService:
    """High-level chat interface consumed by the Streamlit UI."""

    def __init__(self) -> None:
        self.gemini_client = GeminiClient()
        self.nvidia_client = NvidiaClient()
        self.memory = MemoryManager()
        logger.info("ChatService ready with NVIDIA Failover enabled")

    # ── main entry point ────────────────────────────────────────
    def get_response(self, user_message: str) -> str:
        """
        Process a user message and return the advisor's reply.

        Steps:
        1. Check for built-in tool commands (SIP calc, risk profile)
        2. Add user message to memory (triggers profile extraction)
        3. Build system prompt with latest profile
        4. Call Gemini with history
        5. Store response in memory
        6. Return response (or fallback on error)
        """
        # ① Built-in tools
        tool_response = self._check_tool_commands(user_message)
        if tool_response:
            self.memory.add_user_message(user_message)
            self.memory.add_model_message(tool_response)
            return tool_response

        # ② Update memory
        self.memory.add_user_message(user_message)

        # ③ Build prompt
        system_prompt = build_system_prompt(self.memory.profile.to_dict())

        # ④ Call LLM (Gemini Primary -> NVIDIA Fallback)
        try:
            reply = self.gemini_client.send_message(
                message=user_message,
                history=self.memory.get_history()[:-1],  # exclude current msg
                system_instruction=system_prompt,
            )
        except Exception as gemini_exc:
            logger.warning("Gemini LLM failed: %s. Attempting NVIDIA failover...", gemini_exc)
            try:
                reply = self.nvidia_client.send_message(
                    message=user_message,
                    history=self.memory.get_history()[:-1],
                    system_instruction=system_prompt,
                )
            except Exception as nvidia_exc:
                logger.error("Both Gemini and NVIDIA LLMs failed. Showing fallback. NVIDIA Error: %s", nvidia_exc)
                reply = FALLBACK_RESPONSE

        # ⑤ Store model reply
        self.memory.add_model_message(reply)

        return reply

    def reset(self) -> None:
        """Clear session memory."""
        self.memory.clear()

    # ── built-in tool detection ─────────────────────────────────
    def _check_tool_commands(self, text: str) -> str | None:
        lower = text.lower().strip()

        # SIP Calculator
        if lower.startswith("/sip"):
            return self._handle_sip_command(lower)

        # Risk Profile
        if lower.startswith("/risk"):
            return self._handle_risk_command()

        # Profile summary
        if lower.startswith("/profile"):
            return self._handle_profile_command()

        return None

    # ── /sip <amount> <years> <rate> ────────────────────────────
    def _handle_sip_command(self, text: str) -> str:
        """Parse ``/sip <monthly_amount> <years> [rate%]`` and compute."""
        import re

        nums = re.findall(r"[\d.]+", text)
        if len(nums) < 2:
            return (
                "**SIP Calculator** 📊\n\n"
                "Usage: `/sip <monthly_amount> <years> [expected_rate%]`\n\n"
                "Example: `/sip 5000 10 12`  → ₹5,000/month for 10 years at 12 % p.a."
            )

        monthly = float(nums[0])
        years = float(nums[1])
        rate = float(nums[2]) if len(nums) >= 3 else 12.0

        result = sip_calculator(monthly, years, rate)
        return result

    # ── /risk ───────────────────────────────────────────────────
    def _handle_risk_command(self) -> str:
        profile = self.memory.profile
        
        # If no explicit risk level, try to classify based on age/income
        if not profile.risk_level and (profile.age or profile.income):
            age_int = int(profile.age) if profile.age and profile.age.isdigit() else None
            
            # Clean up income string to int if possible (e.g., "80000" -> 80000)
            income_float = None
            if profile.income:
                import re
                nums = re.findall(r"[\d]+", profile.income.replace(',', ''))
                if nums:
                    income_float = float(nums[0])
            
            profile.risk_level = classify_risk(age=age_int, income=income_float)
            logger.info("Auto-classified risk level: %s", profile.risk_level)

        if profile.risk_level:
            level = profile.risk_level.upper()
            return (
                f"**Your Risk Profile: {level}**\n\n"
                f"{_risk_description(profile.risk_level)}"
            )
        return (
            "I haven't determined your risk profile yet. "
            "Tell me about your investment experience, time horizon, "
            "and how you'd feel if your portfolio dropped 20 % in a month."
        )

    # ── /profile ────────────────────────────────────────────────
    def _handle_profile_command(self) -> str:
        d = self.memory.profile.to_dict()
        if not d:
            return "No profile data collected yet. Start chatting and I'll learn about your financial situation! 😊"
        lines = ["**📋 Your Financial Profile**\n"]
        label_map = {
            "income": "💰 Income",
            "goals": "🎯 Goals",
            "risk_level": "⚖️ Risk Level",
            "age": "🎂 Age",
            "dependents": "👨‍👩‍👧 Dependents",
            "existing_investments": "📈 Investments",
        }
        for k, v in d.items():
            label = label_map.get(k, k.title())
            lines.append(f"• {label}: **{v}**")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# Financial calculator utilities
# ═══════════════════════════════════════════════════════════════

def sip_calculator(monthly_investment: float, years: float, annual_rate: float = 12.0) -> str:
    """
    Calculate SIP maturity value using the standard formula:
      FV = P × [((1+r)^n - 1) / r] × (1+r)
    where r = monthly rate, n = total months
    """
    months = int(years * 12)
    monthly_rate = annual_rate / 100 / 12
    total_invested = monthly_investment * months

    if monthly_rate == 0:
        future_value = total_invested
    else:
        future_value = monthly_investment * (
            ((1 + monthly_rate) ** months - 1) / monthly_rate
        ) * (1 + monthly_rate)

    wealth_gained = future_value - total_invested

    return (
        f"**📊 SIP Calculator Results**\n\n"
        f"| Parameter | Value |\n"
        f"|---|---|\n"
        f"| Monthly Investment | ₹{monthly_investment:,.0f} |\n"
        f"| Duration | {years:.0f} years ({months} months) |\n"
        f"| Expected Rate | {annual_rate:.1f}% p.a. |\n"
        f"| **Total Invested** | **₹{total_invested:,.0f}** |\n"
        f"| **Estimated Returns** | **₹{wealth_gained:,.0f}** |\n"
        f"| **Maturity Value** | **₹{future_value:,.0f}** |\n\n"
        f"💡 *The power of compounding: your money grew "
        f"**{future_value / total_invested:.1f}×** over {years:.0f} years!*\n\n"
        f"📌 _Actual returns may vary. Past performance doesn't guarantee future results._"
    )


def classify_risk(age: int | None = None, income: float | None = None) -> str:
    """
    Simple heuristic risk classifier.

    Returns 'low', 'medium', or 'high'.
    """
    score = 50  # start neutral

    if age:
        if age < 30:
            score += 20
        elif age < 45:
            score += 10
        elif age < 55:
            score -= 10
        else:
            score -= 20

    if income:
        if income > 200_000:
            score += 15
        elif income > 100_000:
            score += 5
        elif income < 30_000:
            score -= 15

    if score >= 60:
        return "high"
    elif score >= 40:
        return "medium"
    return "low"


def _risk_description(level: str) -> str:
    descriptions = {
        "low": (
            "🟢 **Conservative Investor**\n\n"
            "You prefer capital preservation over high returns.\n\n"
            "**Recommended allocation:**\n"
            "• 60-70 % Debt (FDs, PPF, Gov bonds)\n"
            "• 20-30 % Large-cap equity / index funds\n"
            "• 5-10 % Gold / liquid funds"
        ),
        "medium": (
            "🟡 **Balanced Investor**\n\n"
            "You're comfortable with moderate ups and downs for better returns.\n\n"
            "**Recommended allocation:**\n"
            "• 40-50 % Equity (large + mid cap)\n"
            "• 30-40 % Debt instruments\n"
            "• 10-15 % Gold / REITs\n"
            "• 5-10 % International funds"
        ),
        "high": (
            "🔴 **Aggressive Investor**\n\n"
            "You can stomach significant volatility for potentially higher gains.\n\n"
            "**Recommended allocation:**\n"
            "• 60-75 % Equity (mid + small cap, sectoral)\n"
            "• 15-25 % Debt for stability\n"
            "• 5-10 % Crypto / alternative assets\n"
            "• 5 % International equity"
        ),
    }
    return descriptions.get(level, "Risk level not determined.")
