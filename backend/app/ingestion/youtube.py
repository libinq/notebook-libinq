import re
import json
import httpx
from typing import Tuple

def extract_youtube_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""

def fetch_youtube_transcript(url: str) -> Tuple[str, str]:
    """
    Attempt to fetch video title and transcript text for a YouTube URL.
    """
    video_id = extract_youtube_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")

    # Fetch title via oEmbed
    title = f"YouTube Video ({video_id})"
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(oembed_url)
            if resp.status_code == 200:
                data = resp.json()
                title = data.get("title", title)
    except Exception:
        pass

    # Try youtube-transcript-api if available, otherwise fetch timedtext API
    transcript_text = ""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh-CN', 'zh', 'en', 'en-US'])
        transcript_text = " ".join([item['text'] for item in transcript_list])
    except Exception:
        # Fallback explanation if transcript api is not installed or video has no captions
        transcript_text = (
            f"[YouTube Video: {title}]\n"
            f"URL: {url}\n"
            f"Video ID: {video_id}\n\n"
            "(Note: Automatic captions could not be fetched directly without API credentials. "
            "Please paste video transcript or notes directly into sources.)"
        )

    return title, transcript_text
