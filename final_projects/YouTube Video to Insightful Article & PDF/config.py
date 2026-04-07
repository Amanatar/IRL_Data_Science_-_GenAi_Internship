"""
config.py — Central configuration for the application.

Loads environment variables and defines constants used across all modules.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ──────────────────────────────────────────────
# API Configuration
# ──────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# The Gemini model to use for text generation
GEMINI_MODEL = "gemini-2.0-flash"

# ──────────────────────────────────────────────
# Application Settings
# ──────────────────────────────────────────────
APP_TITLE = "YouTube → Insightful Article & PDF"
APP_ICON = "🎬"

# Directory where generated outputs (PDFs, text) are saved
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")

# Create the output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ──────────────────────────────────────────────
# LLM Prompt Templates
# ──────────────────────────────────────────────

TITLE_PROMPT = """You are an expert content strategist. Generate a single catchy, SEO-optimized title 
for an article based on this video transcript. The title should be engaging, informative, and 
under 80 characters. Return ONLY the title, no quotes or extra formatting.

Transcript:
{transcript}"""

SUMMARY_PROMPT_SHORT = """You are a professional content writer. Write a concise summary (3-5 sentences) 
of the following video transcript. Focus on the main message and key takeaway.

Transcript:
{transcript}"""

SUMMARY_PROMPT_DETAILED = """You are a professional content writer. Write a detailed summary (8-12 sentences) 
of the following video transcript. Cover all major points discussed, the context, and the conclusions drawn.

Transcript:
{transcript}"""

ARTICLE_PROMPT = """You are an expert journalist and SEO content writer. Transform the following video 
transcript into a well-structured, SEO-optimized article. Follow these guidelines:

1. Write in a professional yet engaging tone
2. Use proper heading hierarchy (## for main sections, ### for subsections)
3. Include an introduction that hooks the reader
4. Break content into logical sections with descriptive headings
5. Use transition sentences between sections
6. Include a compelling conclusion
7. Naturally incorporate relevant keywords for SEO
8. Aim for 800-1500 words
9. Use markdown formatting

Transcript:
{transcript}"""

INSIGHTS_PROMPT = """You are an analytical thinker. Extract 5-8 key insights from this video transcript. 
Each insight should be:
- A clear, actionable bullet point
- 1-2 sentences long
- Focused on a unique takeaway

Format each insight as a bullet point starting with "•". Return ONLY the bullet points.

Transcript:
{transcript}"""
