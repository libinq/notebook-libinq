import re
import json
from typing import List, Dict, Any, Tuple
from ..llm.prompts import PODCAST_PROMPTS
from ..llm.provider import call_llm
from .tts import synthesize_podcast_audio

DURATION_INSTRUCTIONS = {
    "short": "Around 4-6 concise dialogue turns, quick 1-2 minute listen",
    "medium": "Around 10-14 engaging turns, covering key points in 5-8 minutes",
    "long": "Around 20-28 in-depth turns, thorough deep-dive covering all subtleties"
}

def clean_json_response(raw: str) -> List[Dict[str, str]]:
    """Clean markdown code fences and parse JSON array."""
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[len("```json"):].strip()
    elif raw.startswith("```"):
        raw = raw[len("```"):].strip()
    if raw.endswith("```"):
        raw = raw[:-3].strip()

    # Find [ ... ]
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        raw = match.group(0)

    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except Exception:
        pass
        
    # Fallback line parsing
    turns = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            parts = line.split(":", 1)
            turns.append({"speaker": parts[0].strip(), "text": parts[1].strip()})
        else:
            turns.append({"speaker": "Host", "text": line})
    return turns if turns else [{"speaker": "Host", "text": raw}]

async def generate_podcast(
    sources_context: str,
    format_type: str = "deep_dive",
    language: str = "zh",
    duration_mode: str = "medium",
    guidance: str = ""
) -> Tuple[List[Dict[str, str]], str]:
    """
    Generate podcast script and synthesize audio track.
    Returns (script_turns, audio_url).
    """
    prompt_template = PODCAST_PROMPTS.get(format_type, PODCAST_PROMPTS["deep_dive"])
    
    # Speaker name defaults
    if language.startswith("zh") or "chinese" in language.lower():
        speaker_a = "云希 (Host A)"
        speaker_b = "晓晓 (Host B)"
        lang_str = "Chinese (简体中文，口语自然生动)"
    else:
        speaker_a = "Alex (Host A)"
        speaker_b = "Sarah (Host B)"
        lang_str = "English (Conversational, lively, natural)"

    duration_inst = DURATION_INSTRUCTIONS.get(duration_mode, DURATION_INSTRUCTIONS["medium"])
    guidance_str = guidance.strip() if guidance.strip() else "None specified. Cover the most interesting and important insights."

    formatted_prompt = prompt_template.format(
        duration_mode=duration_mode,
        duration_instruction=duration_inst,
        guidance=guidance_str,
        speaker_a=speaker_a,
        speaker_b=speaker_b,
        lang=lang_str,
        sources_context=sources_context
    )

    messages = [
        {"role": "system", "content": "You are an award-winning podcast producer. Output strictly valid JSON."},
        {"role": "user", "content": formatted_prompt}
    ]

    raw_response = await call_llm(messages, temperature=0.7, max_tokens=4096)
    script_turns = clean_json_response(raw_response)

    # Synthesize audio with Edge-TTS
    try:
        audio_url = await synthesize_podcast_audio(script_turns, language=language)
    except Exception as e:
        audio_url = ""

    return script_turns, audio_url
