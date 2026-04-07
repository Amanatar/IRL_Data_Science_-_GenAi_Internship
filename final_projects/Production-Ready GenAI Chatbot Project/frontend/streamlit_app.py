"""
FinWise — AI Financial Advisor  ·  Streamlit Frontend

Run:  streamlit run frontend/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# ── Ensure project root is on sys.path ──────────────────────────
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from backend.chat_service import ChatService
from config.settings import settings

# ═══════════════════════════════════════════════════════════════
# Page config
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="FinWise — AI Financial Advisor",
    page_icon=settings.APP_ICON,
    layout="centered",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# Custom CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Global ─────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Header ─────────────────────────────────────────────────── */
.main-header {
    background: linear-gradient(135deg, #0f4c75 0%, #1b262c 50%, #0f4c75 100%);
    padding: 2rem 2rem 1.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(15, 76, 117, 0.3);
}
.main-header h1 {
    color: #ffffff;
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
}
.main-header p {
    color: #bbe1fa;
    font-size: 1rem;
    margin: 0.5rem 0 0;
    opacity: 0.9;
}

/* ── Chat messages ──────────────────────────────────────────── */
.stChatMessage {
    border-radius: 12px !important;
    margin-bottom: 0.5rem !important;
}

/* ── Sidebar ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1b262c 0%, #0f4c75 100%);
}
[data-testid="stSidebar"] * {
    color: #bbe1fa !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}

/* ── Quick-action buttons ───────────────────────────────────── */
.quick-action {
    background: linear-gradient(135deg, #0f4c75, #3282b8);
    color: white !important;
    border: none;
    padding: 0.6rem 1.2rem;
    border-radius: 25px;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-block;
    margin: 0.25rem;
    text-decoration: none;
}
.quick-action:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(50, 130, 184, 0.4);
}

/* ── Disclaimer banner ──────────────────────────────────────── */
.disclaimer {
    background: rgba(255, 193, 7, 0.1);
    border: 1px solid rgba(255, 193, 7, 0.3);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 0.8rem;
    color: #666;
    margin-top: 1rem;
}

/* ── Tool cards ─────────────────────────────────────────────── */
.tool-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(187,225,250,0.2);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    transition: all 0.3s ease;
}
.tool-card:hover {
    border-color: rgba(187,225,250,0.5);
    background: rgba(255,255,255,0.08);
}
.tool-card h4 { margin: 0 0 0.3rem; font-size: 0.95rem; }
.tool-card p  { margin: 0; font-size: 0.8rem; opacity: 0.7; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# Session state initialisation
# ═══════════════════════════════════════════════════════════════
def _init_session() -> None:
    if "chat_service" not in st.session_state:
        st.session_state.chat_service = ChatService()
    if "messages" not in st.session_state:
        st.session_state.messages = []


_init_session()


# ═══════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════
def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        st.markdown("---")


        # ── Session controls ────────────────────────────────────
        st.markdown("### ⚙️ Session")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_service.reset()
            st.rerun()


        # ── Disclaimer ──────────────────────────────────────────
        st.markdown("---")
        st.caption(settings.DISCLAIMER)


_render_sidebar()


# ═══════════════════════════════════════════════════════════════
# Main chat area
# ═══════════════════════════════════════════════════════════════

# Header
st.markdown("""
<div class="main-header">
    <h1>💰 FinWise — AI Financial Advisor</h1>
    <p>Your intelligent companion for budgeting, investing, and building wealth</p>
</div>
""", unsafe_allow_html=True)

# Welcome message (shown only when history is empty)
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="💰"):
        st.markdown(
            "👋 **Welcome to FinWise!** I'm your AI-powered financial advisor.\n\n"
            "I can help you with:\n"
            "- 📊 **Budgeting** — Create a spending plan that works\n"
            "- 💹 **Investing** — SIPs, mutual funds, stocks explained simply\n"
            "- 🎯 **Goal Planning** — Save for anything from a trip to retirement\n"
            "- ⚖️ **Risk Assessment** — Understand your investor profile\n\n"
            "**Try these quick actions:**"
        )

    # Quick-action buttons
    cols = st.columns(3)
    quick_actions = [
        ("💰 Budget Help", "Help me create a monthly budget. I earn ₹50,000 per month."),
        ("📊 SIP Calculator", "/sip 5000 10 12"),
        ("📈 Start Investing", "I'm a beginner. How do I start investing with ₹5,000?"),
    ]
    for col, (label, prompt) in zip(cols, quick_actions):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()


# ── Render chat history ─────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "💰" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


# ── Chat input ──────────────────────────────────────────────────
if prompt := st.chat_input("Ask me anything about personal finance..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant", avatar="💰"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_service.get_response(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


# ── Footer disclaimer ──────────────────────────────────────────
if st.session_state.messages:
    st.markdown(
        f'<div class="disclaimer">{settings.DISCLAIMER}</div>',
        unsafe_allow_html=True,
    )
