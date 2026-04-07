"""
processing.py — Text cleaning and preprocessing module.

Cleans raw transcript text by removing filler words, fixing formatting,
and preparing the text for LLM processing.
"""

import re


def clean_transcript(text: str) -> str:
    """
    Clean and preprocess raw transcript text.

    Steps:
        1. Remove timestamp artifacts (e.g., [00:01:23])
        2. Remove common filler words/sounds
        3. Fix spacing and punctuation issues
        4. Collapse multiple whitespace
        5. Trim to a reasonable length for LLM processing

    Args:
        text: Raw transcript text.

    Returns:
        Cleaned and preprocessed text string.
    """
    if not text or not text.strip():
        raise ValueError("Transcript text is empty. Cannot process.")

    # Step 1: Remove timestamp artifacts like [00:01:23] or (00:01:23)
    text = re.sub(r"[\[\(]\d{1,2}:\d{2}(?::\d{2})?[\]\)]", "", text)

    # Step 2: Remove common filler words (case-insensitive)
    # Only remove when they appear as standalone words
    filler_words = [
        r"\bum\b", r"\buh\b", r"\bumm\b", r"\buhh\b",
        r"\blike\b(?=\s*,)", r"\byou know\b", r"\bI mean\b",
        r"\bso yeah\b", r"\bbasically\b(?=\s*,)",
    ]
    for filler in filler_words:
        text = re.sub(filler, "", text, flags=re.IGNORECASE)

    # Step 3: Remove auto-generated caption artifacts
    text = re.sub(r"\[Music\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[Applause\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[Laughter\]", "", text, flags=re.IGNORECASE)

    # Step 4: Fix punctuation spacing
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)  # Remove space before punctuation
    text = re.sub(r"([.,!?;:])(\w)", r"\1 \2", text)  # Add space after punctuation

    # Step 5: Collapse multiple whitespace into single space
    text = re.sub(r"\s+", " ", text)

    # Step 6: Trim to ~15,000 words to fit within LLM context limits
    words = text.split()
    MAX_WORDS = 15000
    if len(words) > MAX_WORDS:
        text = " ".join(words[:MAX_WORDS])
        text += "\n\n[Note: Transcript was truncated for processing.]"

    return text.strip()


def get_word_count(text: str) -> int:
    """Return the word count of the given text."""
    return len(text.split())


def estimate_reading_time(text: str, wpm: int = 200) -> int:
    """
    Estimate reading time in minutes.

    Args:
        text: The text to estimate.
        wpm:  Average words per minute (default 200).

    Returns:
        Estimated reading time in minutes (minimum 1).
    """
    word_count = get_word_count(text)
    minutes = max(1, round(word_count / wpm))
    return minutes
