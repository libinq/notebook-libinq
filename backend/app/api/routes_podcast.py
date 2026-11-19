import json
import uuid
import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from ..db import get_connection
from ..config import AUDIO_DIR
from ..podcast.generator import generate_podcast

router = APIRouter(prefix="/api/podcast", tags=["podcast"])

class PodcastGenerateRequest(BaseModel):
    notebook_id: str
    format_type: str = "deep_dive"       # deep_dive | brief | critique | debate
    language: str = "zh"                 # zh | en
    duration_mode: str = "medium"        # short | medium | long
    guidance: Optional[str] = ""
    source_ids: Optional[List[str]] = None

@router.get("")
def list_podcasts(notebook_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM podcasts 
        WHERE notebook_id = ? 
        ORDER BY created_at DESC
    """, (notebook_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    for r in rows:
        try:
            r["script"] = json.loads(r.get("script_json", "[]"))
        except Exception:
            r["script"] = []
    conn.close()
    return {"podcasts": rows}

@router.post("/generate")
async def create_podcast(req: PodcastGenerateRequest):
    conn = get_connection()
    cursor = conn.cursor()

    # Retrieve sources
    if req.source_ids and len(req.source_ids) > 0:
        placeholders = ",".join(["?"] * len(req.source_ids))
        cursor.execute(f"SELECT title, content FROM sources WHERE id IN ({placeholders})", req.source_ids)
    else:
        cursor.execute("SELECT title, content FROM sources WHERE notebook_id = ?", (req.notebook_id,))
    
    sources = cursor.fetchall()
    if not sources:
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot generate podcast without any sources. Please add sources first.")

    # Combine sources text up to 100,000 characters
    source_snippets = []
    total_len = 0
    for s in sources:
        chunk = f"### Source: {s['title']}\n{s['content'][:15000]}"
        source_snippets.append(chunk)
        total_len += len(chunk)
        if total_len > 80000:
            break
    
    sources_context = "\n\n".join(source_snippets)

    # Format human-readable title
    format_names = {
        "deep_dive": "深度对谈 / Deep Dive",
        "brief": "极简速报 / The Brief",
        "critique": "专家评审 / The Critique",
        "debate": "正反辩论 / The Debate"
    }
    title = f"{format_names.get(req.format_type, 'AI Podcast')} - {datetime.datetime.now().strftime('%m-%d %H:%M')}"

    script_turns, audio_url = await generate_podcast(
        sources_context=sources_context,
        format_type=req.format_type,
        language=req.language,
        duration_mode=req.duration_mode,
        guidance=req.guidance or ""
    )

    podcast_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO podcasts (id, notebook_id, title, format_type, language, duration_mode, audio_url, script_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (podcast_id, req.notebook_id, title, req.format_type, req.language, req.duration_mode, audio_url, json.dumps(script_turns), now))

    conn.commit()
    conn.close()

    return {
        "id": podcast_id,
        "title": title,
        "format_type": req.format_type,
        "language": req.language,
        "duration_mode": req.duration_mode,
        "audio_url": audio_url,
        "script": script_turns,
        "created_at": now
    }

@router.get("/audio/{filename}")
def serve_audio(filename: str):
    file_path = AUDIO_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path, media_type="audio/mpeg", filename=filename)

@router.delete("/{podcast_id}")
def delete_podcast(podcast_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT audio_url FROM podcasts WHERE id = ?", (podcast_id,))
    row = cursor.fetchone()
    if row and row["audio_url"]:
        filename = Path(row["audio_url"]).name
        file_path = AUDIO_DIR / filename
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass

    cursor.execute("DELETE FROM podcasts WHERE id = ?", (podcast_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": podcast_id}
