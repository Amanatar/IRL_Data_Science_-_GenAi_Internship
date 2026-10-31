# app.py — The UI
# Streamlit front-end. Handles only presentation and user interaction.

import streamlit as st
from chatbot_engine import create_chat_session, get_response

# ── Page Configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinAdvisor AI",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark premium background */
    .stApp { background-color: #0f1117; }

    /* Chat message bubbles */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 0.5rem 1rem;
        margin-bottom: 0.5rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #161b22;
    }

    /* Title gradient */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6ee7f7, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        text-align: center;
        color: #8b949e;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ─────────────────────────────────────────────────────────
if "chat_session" not in st.session_state:
    st.session_state.chat_session = create_chat_session()

if "messages" not in st.session_state:
    st.session_state.messages = []           # list of {"role": ..., "content": ...}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 FinAdvisor AI")
    st.markdown("*Your Personal Finance Expert*")
    st.divider()
    st.markdown("**How to use:**")
    st.markdown("- Ask about budgeting, savings, or investments")
    st.markdown("- Ask for debt management or tax advice")
    st.markdown("- Request financial goal setting help")
    st.divider()
    st.warning("**Disclaimer:** I am an AI, not a licensed financial advisor. This is for educational purposes only.")
    st.divider()

    if st.button("🗑️ New Chat", use_container_width=True):
        st.session_state.chat_session = create_chat_session()
        st.session_state.messages = []
        st.rerun()

    st.caption("Powered by Google Gemini 1.5 Flash")

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">FinAdvisor AI 🏦</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Your personal finance expert — ask me anything about your financial journey</p>',
    unsafe_allow_html=True,
)

# ── Chat History Render ────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Welcome Message (first load) ───────────────────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 Hi there! I'm **FinAdvisor AI**. I'm here to help you manage your personal finances.\n\n"
            "You can ask me about:\n"
            "- 📊 Budgeting & Expense tracking\n"
            "- 📈 Investment basics\n"
            "- 🏦 Retirement planning\n"
            "- 💸 Debt management\n"
            "- 🏠 Financial goal setting\n\n"
            "What financial question can I help you with today?"
        )

# ── Input Handling ─────────────────────────────────────────────────────────────
if user_input := st.chat_input("Ask about budgeting, investing, or taxes…"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            reply = get_response(st.session_state.chat_session, user_input)
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
