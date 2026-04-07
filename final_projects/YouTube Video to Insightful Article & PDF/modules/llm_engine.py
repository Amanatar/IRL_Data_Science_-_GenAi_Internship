"""
llm_engine.py — LLM-powered content generation module.

Uses Google Gemini via LangChain to generate titles, summaries,
articles, and key insights from video transcripts.
"""

from dataclasses import dataclass
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

import config


@dataclass
class GeneratedContent:
    """Container for all LLM-generated content."""
    title: str
    summary: str
    article: str
    insights: str
    summary_style: str  # "short" or "detailed"


def _get_llm() -> ChatGoogleGenerativeAI:
    """
    Initialize and return the Gemini LLM instance.

    Raises:
        ValueError: If the API key is not configured.
    """
    if not config.GOOGLE_API_KEY:
        raise ValueError(
            "Google API key not found. Please set GOOGLE_API_KEY in your .env file.\n"
            "Get a free key at: https://aistudio.google.com/app/apikey"
        )

    return ChatGoogleGenerativeAI(
        model=config.GEMINI_MODEL,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=0.7,
        max_output_tokens=4096,
    )


def _run_chain(prompt_template: str, transcript: str, max_retries: int = 3) -> str:
    """
    Run a single LLM chain with the given prompt and transcript.
    Includes an automatic retry mechanism for 429 Quota Exhausted limits.

    Args:
        prompt_template: The prompt template string with {transcript} placeholder.
        transcript:      The cleaned transcript text.
        max_retries:     Number of times to retry if a rate limit error is encountered.

    Returns:
        The LLM's response as a string.
    """
    import time
    llm = _get_llm()
    prompt = PromptTemplate(
        input_variables=["transcript"],
        template=prompt_template,
    )
    chain = prompt | llm | StrOutputParser()
    
    for attempt in range(max_retries):
        try:
            result = chain.invoke({"transcript": transcript})
            return result.strip()
        except Exception as e:
            # Check if this is a quota/rate limit error
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt < max_retries - 1:
                    # Sleep for 25s first retry, 50s next retry
                    sleep_time = 25 * (attempt + 1)
                    print(f"Rate limit hit. Retrying in {sleep_time} seconds (Attempt {attempt + 1}/{max_retries - 1})...")
                    time.sleep(sleep_time)
                    continue
            # If not a rate limit error, or out of retries, raise it
            raise e


def generate_title(transcript: str) -> str:
    """Generate a catchy, SEO-optimized title from the transcript."""
    return _run_chain(config.TITLE_PROMPT, transcript)


def generate_summary(transcript: str, style: str = "short") -> str:
    """
    Generate a summary from the transcript.

    Args:
        transcript: Cleaned transcript text.
        style:      "short" for 3-5 sentences, "detailed" for 8-12 sentences.

    Returns:
        Summary text.
    """
    if style == "detailed":
        return _run_chain(config.SUMMARY_PROMPT_DETAILED, transcript)
    return _run_chain(config.SUMMARY_PROMPT_SHORT, transcript)


def generate_article(transcript: str) -> str:
    """Generate a full, SEO-optimized article from the transcript."""
    return _run_chain(config.ARTICLE_PROMPT, transcript)


def generate_insights(transcript: str) -> str:
    """Extract key insights as bullet points from the transcript."""
    return _run_chain(config.INSIGHTS_PROMPT, transcript)


def generate_all_content(
    transcript: str, summary_style: str = "short"
) -> GeneratedContent:
    """
    Generate all content pieces from the transcript.

    This is the main entry point for the LLM engine. It generates:
        - A catchy title
        - A summary (short or detailed)
        - A full article
        - Key insights

    Args:
        transcript:    Cleaned transcript text.
        summary_style: "short" or "detailed" summary style.

    Returns:
        GeneratedContent dataclass with all generated pieces.
    """
    title = generate_title(transcript)
    summary = generate_summary(transcript, style=summary_style)
    article = generate_article(transcript)
    insights = generate_insights(transcript)

    return GeneratedContent(
        title=title,
        summary=summary,
        article=article,
        insights=insights,
        summary_style=summary_style,
    )
