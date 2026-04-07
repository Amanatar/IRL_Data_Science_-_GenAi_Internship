"""
transcript.py — YouTube transcript extraction module.

Handles URL parsing, video ID extraction, and transcript fetching
using the youtube-transcript-api library.
"""

import re
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract the YouTube video ID from various URL formats.

    Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/v/VIDEO_ID
        - https://m.youtube.com/watch?v=VIDEO_ID

    Args:
        url: The YouTube URL string.

    Returns:
        The video ID string if found, None otherwise.
    """
    # Patterns ordered from most specific to least specific
    patterns = [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:m\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def fetch_transcript(video_id: str, languages: list[str] = None) -> str:
    """
    Fetch the transcript for a YouTube video.

    Tries to get the transcript in the preferred languages first,
    then falls back to any available transcript.

    Args:
        video_id:  The YouTube video ID.
        languages: Preferred language codes (e.g., ["en", "hi"]).
                   Defaults to ["en"] if not specified.

    Returns:
        The full transcript as a single string.

    Raises:
        ValueError: If no transcript is available for the video.
        ConnectionError: If there's a network issue fetching the transcript.
    """
    if languages is None:
        languages = ["en"]

    api = YouTubeTranscriptApi()
    
    try:
        if languages:
            transcript_list = api.fetch(video_id, languages=languages)
        else:
            transcript_list = api.fetch(video_id)
    except Exception:
        try:
            # Fallback: get transcript in any available language
            available = api.list(video_id)
            transcript_obj = next(iter(available))
            transcript_list = transcript_obj.fetch()
        except Exception as e:
            raise ValueError(
                f"Could not retrieve transcript for video '{video_id}'. "
                f"The video may not have captions enabled. Error: {e}"
            )

    # Combine all transcript segments into one string
    full_text = " ".join(segment.text if hasattr(segment, 'text') else segment["text"] for segment in transcript_list)
    return full_text


def get_transcript_from_url(url: str) -> tuple[str, str]:
    """
    High-level function: extract transcript from a YouTube URL.

    Args:
        url: The YouTube URL.

    Returns:
        A tuple of (video_id, transcript_text).

    Raises:
        ValueError: If the URL is invalid or transcript is unavailable.
    """
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(
            "Invalid YouTube URL. Please provide a valid link like:\n"
            "https://www.youtube.com/watch?v=VIDEO_ID"
        )

    transcript = fetch_transcript(video_id)
    return video_id, transcript
