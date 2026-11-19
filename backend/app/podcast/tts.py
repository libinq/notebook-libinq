import os
import uuid
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..config import AUDIO_DIR

# Voice Mappings for bilingual natural conversation
VOICE_MAP = {
    "zh": {
        "speaker_a": "zh-CN-YunxiNeural",      # 云希：活力生动男声
        "speaker_b": "zh-CN-XiaoxiaoNeural",   # 晓晓：温婉亲切女声
        "narrator": "zh-CN-YunyangNeural"      # 云扬：专业播报
    },
    "en": {
        "speaker_a": "en-US-GuyNeural",         # Guy: Dynamic male host
        "speaker_b": "en-US-JennyNeural",       # Jenny: Sharp female host
        "narrator": "en-US-AndrewNeural"        # Andrew: Warm narrator
    }
}

async def generate_speech_edge_tts(text: str, voice: str, output_path: Path):
    """Generate audio snippet using Edge-TTS."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))

def concatenate_mp3_files(input_files: List[Path], output_file: Path):
    """Concatenate multiple mp3 clips into one continuous podcast track."""
    try:
        from pydub import AudioSegment
        combined = AudioSegment.empty()
        # 300ms pause between turns
        silence = AudioSegment.silent(duration=350)
        
        for file in input_files:
            if file.exists() and file.stat().st_size > 0:
                segment = AudioSegment.from_file(str(file), format="mp3")
                combined += segment + silence
                
        combined.export(str(output_file), format="mp3", bitrate="128k")
    except Exception:
        # Fallback raw binary concatenation (standard MP3 frames can be concatenated directly)
        with open(output_file, 'wb') as outfile:
            for file in input_files:
                if file.exists() and file.stat().st_size > 0:
                    with open(file, 'rb') as infile:
                        outfile.write(infile.read())

async def synthesize_podcast_audio(script: List[Dict[str, str]], language: str = "zh") -> str:
    """
    Synthesize complete podcast audio from script turns.
    Returns relative URL path to generated MP3 file.
    """
    lang_key = "zh" if language.lower().startswith("zh") or "chinese" in language.lower() else "en"
    voices = VOICE_MAP[lang_key]
    
    episode_id = str(uuid.uuid4())
    temp_dir = AUDIO_DIR / episode_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    snippet_files = []
    
    try:
        for idx, turn in enumerate(script):
            speaker_name = turn.get("speaker", "").lower()
            text = turn.get("text", "").strip()
            if not text:
                continue
                
            # Assign voice based on speaker role
            if "host a" in speaker_name or "alex" in speaker_name or "云希" in speaker_name or "正方" in speaker_name or idx % 2 == 0:
                voice = voices["speaker_a"]
            elif "host b" in speaker_name or "sarah" in speaker_name or "晓晓" in speaker_name or "反方" in speaker_name or idx % 2 == 1:
                voice = voices["speaker_b"]
            else:
                voice = voices["narrator"]

            snippet_path = temp_dir / f"turn_{idx:03d}.mp3"
            await generate_speech_edge_tts(text, voice, snippet_path)
            snippet_files.append(snippet_path)

        final_mp3_name = f"podcast_{episode_id}.mp3"
        final_mp3_path = AUDIO_DIR / final_mp3_name
        concatenate_mp3_files(snippet_files, final_mp3_path)
        
        return f"/api/podcast/audio/{final_mp3_name}"
    finally:
        # Clean up temporary snippets
        for file in snippet_files:
            try:
                if file.exists():
                    file.unlink()
            except Exception:
                pass
        try:
            temp_dir.rmdir()
        except Exception:
            pass
