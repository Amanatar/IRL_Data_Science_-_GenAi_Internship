"""
app.py — Main Streamlit application for YouTube → Insightful Article & PDF.

This is the entry point. Run with:
    streamlit run app.py
"""

import os
import time
import streamlit as st

# ──────────────────────────────────────────────
# Page Configuration (must be first Streamlit call)
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="YouTube → Insightful Article & PDF",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

import config
from modules.transcript import get_transcript_from_url, extract_video_id
from modules.processing import clean_transcript, get_word_count, estimate_reading_time
from modules.llm_engine import generate_all_content
from modules.pdf_generator import create_pdf


# ──────────────────────────────────────────────
# Custom CSS for premium styling
# ──────────────────────────────────────────────
def inject_custom_css():
    st.markdown("""
    <style>
        /* ── Import Google Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

        /* ── Global Overrides ── */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #e2e8f0;
        }
        h1, h2, h3, h4, h5, h6, .hero-title {
            font-family: 'Outfit', sans-serif !important;
        }

        /* ── Dark App Theme ── */
        .stApp {
            background: linear-gradient(145deg, #0f111a 0%, #1e1b4b 100%);
            background-attachment: fixed;
        }
        
        /* Stop Streamlit block color mismatch */
        .main {
            background: transparent !important;
        }
        
        div[data-testid="stToolbar"] {
            display: none;
        }

        /* ── Main container ── */
        .main .block-container {
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 5rem;
        }

        /* ── Hero Section ── */
        .hero-container {
            background: rgba(30, 41, 59, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border-radius: 28px;
            padding: 4.5rem 2.5rem;
            margin-bottom: 3.5rem;
            text-align: center;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.15);
            position: relative;
            overflow: visible;
        }
        
        /* Animated Glowing Backdrop */
        .hero-container::before {
            content: '';
            position: absolute;
            top: -2px; left: -2px; right: -2px; bottom: -2px;
            background: linear-gradient(45deg, #ff007f, #7928ca, #ff007f, #4f46e5);
            background-size: 400%;
            z-index: -1;
            filter: blur(24px);
            animation: glowing 15s ease infinite;
            opacity: 0.6;
            border-radius: 30px;
        }
        @keyframes glowing {
            0% { background-position: 0 0; }
            50% { background-position: 400% 0; }
            100% { background-position: 0 0; }
        }

        .hero-title {
            font-size: 3.8rem;
            font-weight: 800;
            background: linear-gradient(to right, #ffffff, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 0 1rem 0;
            letter-spacing: -1.5px;
            text-shadow: 0 0 40px rgba(165, 180, 252, 0.1);
        }
        .hero-subtitle {
            font-size: 1.25rem;
            color: #cbd5e1;
            font-weight: 300;
            max-width: 750px;
            margin: 0 auto;
            line-height: 1.6;
        }

        /* ── Input Fields override ── */
        .stTextInput div[data-baseweb="input"] {
            background: rgba(15, 23, 42, 0.5) !important;
            border: 1px solid rgba(148, 163, 184, 0.2) !important;
            border-radius: 16px !important;
            padding: 0.25rem !important;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease !important;
        }
        .stTextInput input {
            color: #fff !important;
            font-size: 1.1rem !important;
        }
        .stTextInput div[data-baseweb="input"]:focus-within {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2) !important;
            background: rgba(15, 23, 42, 0.8) !important;
        }
        
        /* Force label colors */
        .stTextInput label, .stSelectbox label {
            color: #cbd5e1 !important;
            font-family: 'Outfit', sans-serif;
            font-size: 1.05rem !important;
            font-weight: 500 !important;
        }

        /* ── Feature Cards ── */
        .feature-row {
            display: flex;
            gap: 1.25rem;
            margin: 2rem 0;
            flex-wrap: wrap;
        }
        .feature-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(16px);
            border-radius: 20px;
            padding: 2rem 1.5rem;
            flex: 1;
            min-width: 220px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .feature-card::after {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            opacity: 0;
            transition: opacity 0.4s ease;
        }
        .feature-card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
            border-color: rgba(139, 92, 246, 0.5);
            background: rgba(30, 41, 59, 0.7);
        }
        .feature-card:hover::after {
            opacity: 1;
        }
        .feature-icon { 
            font-size: 2.8rem; 
            margin-bottom: 1.2rem;
            display: inline-block;
            filter: drop-shadow(0 0 15px rgba(255,255,255,0.1));
            transition: transform 0.4s ease;
        }
        .feature-card:hover .feature-icon {
            transform: scale(1.15) rotate(5deg);
            filter: drop-shadow(0 0 20px rgba(165, 180, 252, 0.5));
        }
        .feature-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #f8fafc;
            margin: 0.5rem 0;
        }
        .feature-desc {
            font-size: 0.9rem;
            color: #94a3b8;
            line-height: 1.6;
        }

        /* ── Content Cards ── */
        .content-card {
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 2.5rem;
            margin: 2rem 0;
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
            color: #f1f5f9;
            transition: box-shadow 0.3s ease, border-color 0.3s ease;
        }
        .content-card:hover {
            border-color: rgba(99, 102, 241, 0.3);
            box-shadow: 0 20px 50px rgba(0,0,0,0.4);
        }
        .content-card h3 {
            color: #a5b4fc;
            font-weight: 700;
            margin-bottom: 1.5rem;
            font-size: 1.75rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            padding-bottom: 1rem;
        }
        .content-card p {
            line-height: 1.8;
            font-size: 1.05rem;
            color: #cbd5e1;
        }
        
        /* ── Markdown styling within Content Cards ── */
        .content-card h1, .content-card h2, .content-card h4 {
            color: #f8fafc;
        }
        .content-card ul, .content-card ol {
            color: #cbd5e1;
            line-height: 1.8;
        }
        .content-card li {
            margin-bottom: 0.5rem;
        }

        /* ── Stat Pill ── */
        .stat-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.3);
            font-size: 0.85rem;
            font-weight: 600;
            padding: 0.4rem 1.25rem;
            border-radius: 999px;
            margin: 0.25rem;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }
        .stat-pill:hover {
            background: rgba(99, 102, 241, 0.25);
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.2);
            transform: translateY(-2px);
        }

        /* ── Sidebar styling ── */
        section[data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.7) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown li,
        section[data-testid="stSidebar"] label {
            color: #cbd5e1 !important;
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #ffffff !important;
            font-family: 'Outfit', sans-serif !important;
        }

        /* ── Processing Steps/Badges ── */
        .step-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #a855f7);
            color: white;
            font-weight: 700;
            font-size: 0.9rem;
            margin-right: 0.75rem;
            box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3);
        }
        .step-text {
            font-size: 1.05rem;
            color: #f1f5f9;
            font-weight: 500;
        }

        /* ── Button overrides ── */
        .stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 16px !important;
            padding: 0.9rem 2.5rem !important;
            font-weight: 600 !important;
            font-size: 1.15rem !important;
            letter-spacing: 0.5px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
            width: 100% !important;
        }
        .stButton > button:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 15px 30px rgba(99, 102, 241, 0.6) !important;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        }
        
        /* ── Expander styling ── */
        .streamlit-expanderHeader {
            font-weight: 600 !important;
            color: #a5b4fc !important;
            background: rgba(15, 23, 42, 0.4) !important;
            border-radius: 12px;
        }
        div[data-testid="stExpander"] {
            background: rgba(15, 23, 42, 0.4) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }

        /* ── Download button ── */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
        }
        .stDownloadButton > button:hover {
            box-shadow: 0 15px 30px rgba(16, 185, 129, 0.5) !important;
            background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        }

        /* Fix Streamlit Warning Colors in Dark Theme */
        .stAlert {
            background-color: rgba(255, 193, 7, 0.1) !important;
            color: #fbbf24 !important;
            border: 1px solid rgba(251, 191, 36, 0.3) !important;
            border-radius: 12px !important;
        }
        .stAlert[data-baseweb="notification"] {
            background-color: rgba(239, 68, 68, 0.1) !important;
            color: #f87171 !important;
            border: 1px solid rgba(239, 68, 68, 0.3) !important;
        }
        
        /* Loading Spinner Color Override */
        .stSpinner > div > div {
            border-color: #8b5cf6 !important;
            border-bottom-color: transparent !important;
        }
    </style>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# UI Components
# ──────────────────────────────────────────────

def render_hero():
    """Render the hero section at the top of the page."""
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🎬 YouTube → Insightful Article & PDF</div>
        <div class="hero-subtitle">
            Transform any YouTube video into a polished, SEO-optimized article
            with key insights and a downloadable PDF — powered by AI.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_features():
    """Render the feature cards below the hero."""
    st.markdown("""
    <div class="feature-row">
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <div class="feature-title">Smart Transcription</div>
            <div class="feature-desc">Auto-extracts and cleans YouTube captions</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI Article Writer</div>
            <div class="feature-desc">Generates polished, structured articles</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">💡</div>
            <div class="feature-title">Key Insights</div>
            <div class="feature-desc">Extracts actionable takeaways</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">PDF Export</div>
            <div class="feature-desc">Professional downloadable document</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with settings and instructions."""
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        st.markdown("---")

        # Summary style selector
        summary_style = st.radio(
            "📏 Summary Style",
            options=["short", "detailed"],
            format_func=lambda x: "🔹 Short (3-5 sentences)" if x == "short" else "🔸 Detailed (8-12 sentences)",
            index=0,
            help="Choose how detailed the summary should be.",
        )

        st.markdown("---")
        st.markdown("## 📖 How to Use")
        st.markdown("""
        1. Paste a YouTube URL below
        2. Choose your summary style
        3. Click **Generate Article**
        4. Download the PDF!
        """)



        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; opacity: 0.5; font-size: 0.75rem;'>"
            "Built with ❤️ using Streamlit & Gemini"
            "</p>",
            unsafe_allow_html=True,
        )

    return summary_style


def render_results(content, video_url: str, video_id: str):
    """
    Render the generated content in a beautiful layout.

    Args:
        content:   GeneratedContent dataclass.
        video_url: Original YouTube URL.
        video_id:  YouTube video ID.
    """
    # ── Title ──
    st.markdown(f"""
    <div class="content-card" style="background: linear-gradient(135deg, #EEF2FF, #FDF2F8); border: none;">
        <h2 style="text-align: center; color: #1F2937; font-weight: 800; font-size: 1.8rem; margin: 0;">
            {content.title}
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats row ──
    article_words = get_word_count(content.article)
    read_time = estimate_reading_time(content.article)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-pill">📊 {article_words} words</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-pill">⏱️ {read_time} min read</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-pill">📏 {content.summary_style.title()} summary</div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-pill">🎥 Video: {video_id}</div>', unsafe_allow_html=True)

    st.markdown("")

    # ── Summary ──
    st.markdown(f"""
    <div class="content-card">
        <h3>📋 Summary</h3>
        <p style="color: #374151; line-height: 1.8; font-size: 1rem;">{content.summary}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Full Article ──
    with st.expander("📰 Read Full Article", expanded=True):
        st.markdown(content.article)

    # ── Key Insights ──
    st.markdown(f"""
    <div class="content-card" style="border-left: 4px solid #4F46E5;">
        <h3>💡 Key Insights</h3>
        <div style="color: #374151; line-height: 2; font-size: 0.95rem;">
            {content.insights.replace(chr(10), '<br>')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # ── PDF Generation & Download ──
    with st.spinner("📄 Generating PDF..."):
        pdf_path = create_pdf(
            title=content.title,
            summary=content.summary,
            article=content.article,
            insights=content.insights,
            video_url=video_url,
            video_id=video_id,
        )

    # Read the PDF file for download
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.download_button(
            label="⬇️  Download PDF",
            data=pdf_bytes,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf",
        )
    with col_b:
        st.success(f"✅ PDF saved to: `{pdf_path}`")

    # ── Save raw text outputs locally ──
    _save_text_outputs(content, video_id)


def _save_text_outputs(content, video_id: str):
    """Save raw text outputs to the outputs directory for later reference."""
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    text_path = os.path.join(config.OUTPUT_DIR, f"article_{video_id}_{timestamp}.md")

    with open(text_path, "w", encoding="utf-8") as f:
        f.write(f"# {content.title}\n\n")
        f.write(f"## Summary\n\n{content.summary}\n\n")
        f.write(f"## Article\n\n{content.article}\n\n")
        f.write(f"## Key Insights\n\n{content.insights}\n")


# ──────────────────────────────────────────────
# Main Application Logic
# ──────────────────────────────────────────────

def main():
    """Main application entry point."""
    # Inject premium CSS
    inject_custom_css()

    # Render hero and features
    render_hero()
    render_features()

    # Sidebar settings
    summary_style = render_sidebar()

    # ── Input Section ──
    st.markdown("---")
    st.markdown("### 🔗 Enter YouTube Video URL")

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
        )
    with col_btn:
        generate_btn = st.button("🚀 Generate", use_container_width=True)

    # ── Processing Pipeline ──
    if generate_btn and youtube_url:
        try:
            # Step 1: Extract transcript
            with st.status("🔄 Processing your video...", expanded=True) as status:
                st.write("📡 **Step 1/4** — Extracting transcript from YouTube...")
                video_id, raw_transcript = get_transcript_from_url(youtube_url)
                st.write(f"✅ Transcript extracted — {get_word_count(raw_transcript)} words")

                # Step 2: Clean transcript
                st.write("🧹 **Step 2/4** — Cleaning and preprocessing text...")
                clean_text = clean_transcript(raw_transcript)
                st.write(f"✅ Text cleaned — {get_word_count(clean_text)} words")

                # Step 3: Generate content with LLM
                st.write("🤖 **Step 3/4** — AI is writing your article...")
                content = generate_all_content(clean_text, summary_style=summary_style)
                st.write("✅ Article, summary, and insights generated")

                # Step 4: Finalize
                st.write("📄 **Step 4/4** — Preparing output...")
                time.sleep(0.5)  # Small delay for visual feedback
                status.update(label="✅ Processing complete!", state="complete")

            # Display results
            st.markdown("---")
            render_results(content, youtube_url, video_id)

        except ValueError as e:
            st.error(f"⚠️ {e}")
        except Exception as e:
            st.error(
                f"❌ An unexpected error occurred: {e}\n\n"
                "**Troubleshooting tips:**\n"
                "- Check that your YouTube URL is valid\n"
                "- Ensure the video has captions/subtitles enabled\n"
                "- Verify your Google API key is correct\n"
                "- Check your internet connection"
            )

    elif generate_btn and not youtube_url:
        st.warning("⚠️ Please enter a YouTube URL first.")


if __name__ == "__main__":
    main()
