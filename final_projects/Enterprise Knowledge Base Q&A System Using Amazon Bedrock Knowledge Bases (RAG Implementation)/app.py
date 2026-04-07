"""
Streamlit Frontend — Enterprise Knowledge Base Q&A System.

A ChatGPT-style interface for querying Amazon Bedrock Knowledge Bases
with source citations and conversation history.
"""

import streamlit as st
import logging
import time
from backend import BedrockRAGClient, RAGResponse

logger = logging.getLogger(__name__)

# ── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Enterprise Knowledge Base Q&A",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS for Premium UI ───────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global Styles ── */
    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0d0d2b 100%);
    }

    /* ── Header ── */
    .main-header {
        text-align: center;
        padding: 2rem 1rem 1rem;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .main-header p {
        color: #8b8fa3;
        font-size: 1rem;
        font-weight: 300;
    }

    /* ── Chat Container ── */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 0 1rem;
    }

    /* ── Message Bubbles ── */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        padding: 1rem 1.4rem;
        border-radius: 20px 20px 4px 20px;
        margin: 0.8rem 0;
        max-width: 80%;
        margin-left: auto;
        font-size: 0.95rem;
        line-height: 1.6;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        word-wrap: break-word;
    }
    .assistant-message {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #e0e0e8;
        padding: 1.2rem 1.4rem;
        border-radius: 20px 20px 20px 4px;
        margin: 0.8rem 0;
        max-width: 85%;
        font-size: 0.95rem;
        line-height: 1.7;
        backdrop-filter: blur(10px);
        word-wrap: break-word;
    }

    /* ── Message Labels ── */
    .msg-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.3rem;
        opacity: 0.7;
    }
    .msg-label-user { color: #c4b5fd; text-align: right; }
    .msg-label-assistant { color: #94a3b8; }

    /* ── Citation Cards ── */
    .citation-container {
        margin-top: 1rem;
        padding-top: 0.8rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    .citation-header {
        font-size: 0.78rem;
        font-weight: 600;
        color: #667eea;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.6rem;
    }
    .citation-card {
        background: rgba(102, 126, 234, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.15);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    .citation-card:hover {
        background: rgba(102, 126, 234, 0.14);
        border-color: rgba(102, 126, 234, 0.3);
        transform: translateY(-1px);
    }
    .citation-source {
        font-size: 0.78rem;
        font-weight: 600;
        color: #a78bfa;
        margin-bottom: 0.3rem;
    }
    .citation-text {
        font-size: 0.82rem;
        color: #94a3b8;
        line-height: 1.5;
    }

    /* ── Error Message ── */
    .error-message {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #fca5a5;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        font-size: 0.9rem;
    }

    /* ── Hide Sidebar Completely ── */
    [data-testid="stSidebar"] { display: none !important; }
    .stSidebar { display: none !important; }
    button[kind="header"] { display: none !important; }

    /* ── Input Field Styling ── */
    .stChatInput > div {
        border-radius: 16px !important;
    }

    /* ── Loading Animation ── */
    .thinking-dots {
        display: inline-flex;
        gap: 4px;
        padding: 0.5rem 0;
    }
    .thinking-dots span {
        width: 8px;
        height: 8px;
        background: #667eea;
        border-radius: 50%;
        animation: thinking 1.4s ease-in-out infinite;
    }
    .thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
    .thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes thinking {
        0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
        40% { opacity: 1; transform: scale(1.1); }
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.5);
    }

    /* ── Hide default Streamlit branding ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Session State Initialization ────────────────────────────────────────────

def init_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "client" not in st.session_state:
        st.session_state.client = None
    if "client_error" not in st.session_state:
        st.session_state.client_error = None
    if "total_queries" not in st.session_state:
        st.session_state.total_queries = 0


def get_client() -> BedrockRAGClient | None:
    """Lazily initialize and cache the Bedrock client."""
    if st.session_state.client is None and st.session_state.client_error is None:
        try:
            st.session_state.client = BedrockRAGClient()
            st.session_state.client_error = None
        except Exception as e:
            st.session_state.client_error = str(e)
            logger.error("Failed to initialize client: %s", e)
    return st.session_state.client


# ── UI Components ───────────────────────────────────────────────────────────

def render_header():
    """Render the main application header."""
    st.markdown("""
    <div class="main-header">
        <h1>🧠 Enterprise Knowledge Base</h1>
        <p>Powered by Amazon Bedrock &bull; RAG-based Q&A System</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Sidebar removed per user request."""
    pass


def render_message(role: str, content: str, citations: list | None = None):
    """Render a single chat message with optional citations."""
    if role == "user":
        st.markdown(f"""
        <div class="msg-label msg-label-user">You</div>
        <div class="user-message">{content}</div>
        """, unsafe_allow_html=True)
    else:
        citations_html = ""
        if citations:
            # De-duplicate citations by source URI
            seen = set()
            unique_citations = []
            for c in citations:
                key = c.get("source_uri", "") or c.get("source_name", "")
                if key and key not in seen:
                    seen.add(key)
                    unique_citations.append(c)

            if unique_citations:
                citation_cards = ""
                for i, c in enumerate(unique_citations, 1):
                    name = c.get("display_name", "Unknown Source")
                    text = c.get("text", "")
                    # Truncate for display
                    display_text = text[:200] + "..." if len(text) > 200 else text
                    citation_cards += f"""
                    <div class="citation-card">
                        <div class="citation-source">📄 [{i}] {name}</div>
                        <div class="citation-text">{display_text}</div>
                    </div>
                    """
                citations_html = f"""
                <div class="citation-container">
                    <div class="citation-header">📚 Source Citations ({len(unique_citations)})</div>
                    {citation_cards}
                </div>
                """

        st.markdown(f"""
        <div class="msg-label msg-label-assistant">Assistant</div>
        <div class="assistant-message">
            {content}
            {citations_html}
        </div>
        """, unsafe_allow_html=True)


def render_chat_history():
    """Render all messages in the conversation history."""
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        render_message(
            role=msg["role"],
            content=msg["content"],
            citations=msg.get("citations"),
        )
    st.markdown('</div>', unsafe_allow_html=True)


def process_query(user_query: str):
    """Process a user query through the RAG pipeline."""
    client = get_client()
    if not client:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "⚠️ Unable to connect to Amazon Bedrock. Please check your AWS configuration.",
        })
        return

    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Show thinking animation
    with st.spinner(""):
        st.markdown("""
        <div class="assistant-message" style="max-width: 200px;">
            <div class="thinking-dots">
                <span></span><span></span><span></span>
            </div>
            Searching knowledge base...
        </div>
        """, unsafe_allow_html=True)

        # Query the backend
        start_time = time.time()
        response: RAGResponse = client.query(
            user_query=user_query,
            session_id=st.session_state.session_id,
        )
        elapsed = time.time() - start_time
        logger.info("Query completed in %.2fs", elapsed)

    # Update session ID for multi-turn
    if response.session_id:
        st.session_state.session_id = response.session_id

    # Handle errors
    if response.is_error:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"⚠️ {response.error_message}",
        })
    else:
        # Prepare citations for storage
        citation_data = [
            {
                "text": c.text,
                "source_uri": c.source_uri,
                "source_name": c.source_name,
                "display_name": c.display_name,
                "score": c.score,
            }
            for c in response.citations
        ]

        st.session_state.messages.append({
            "role": "assistant",
            "content": response.answer,
            "citations": citation_data,
        })

    st.session_state.total_queries += 1


# ── Main Application ────────────────────────────────────────────────────────

def main():
    """Main application entry point."""
    init_session_state()
    render_header()
    # Sidebar removed per user request
    # Initialize client silently
    get_client()

    # Render conversation history
    render_chat_history()

    # Welcome message if no messages
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-container">
            <div class="assistant-message" style="text-align: center; max-width: 600px; margin: 2rem auto;">
                <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">👋</div>
                <div style="font-size: 1.1rem; font-weight: 500; color: #e0e0e8; margin-bottom: 0.5rem;">
                    Welcome to Enterprise Knowledge Base
                </div>
                <div style="font-size: 0.88rem; color: #8b8fa3; line-height: 1.6;">
                    Ask me anything about your organization's documents.<br>
                    I'll search the knowledge base and provide answers with source citations.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input(
        placeholder="Ask a question about your documents...",
        key="chat_input",
    )

    if user_input:
        process_query(user_input)
        st.rerun()


if __name__ == "__main__":
    main()
