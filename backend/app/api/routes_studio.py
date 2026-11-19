import json
import uuid
import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from ..db import get_connection
from ..config import UPLOAD_DIR
from ..studio.artifacts import generate_studio_artifact

router = APIRouter(prefix="/api/studio", tags=["studio"])

class StudioGenerateRequest(BaseModel):
    notebook_id: str
    artifact_type: str                 # mindmap | briefing | study_guide | faq | timeline | quiz | flashcards | presentation
    language: str = "zh"               # zh | en
    source_ids: Optional[List[str]] = None

@router.get("")
def list_artifacts(notebook_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM studio_artifacts 
        WHERE notebook_id = ? 
        ORDER BY created_at DESC
    """, (notebook_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    for r in rows:
        try:
            r["content"] = json.loads(r["content_json"])
        except Exception:
            r["content"] = r["content_json"]
    conn.close()
    return {"artifacts": rows}

@router.post("/generate")
async def create_artifact(req: StudioGenerateRequest):
    conn = get_connection()
    cursor = conn.cursor()

    if req.source_ids and len(req.source_ids) > 0:
        placeholders = ",".join(["?"] * len(req.source_ids))
        cursor.execute(f"SELECT title, content FROM sources WHERE id IN ({placeholders})", req.source_ids)
    else:
        cursor.execute("SELECT title, content FROM sources WHERE notebook_id = ?", (req.notebook_id,))
    
    sources = cursor.fetchall()
    if not sources:
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot generate studio artifact without any sources. Please add sources first.")

    source_snippets = []
    total_len = 0
    for s in sources:
        chunk = f"### Source: {s['title']}\n{s['content'][:15000]}"
        source_snippets.append(chunk)
        total_len += len(chunk)
        if total_len > 80000:
            break
    
    sources_context = "\n\n".join(source_snippets)

    titles_map = {
        "mindmap": "思维导图 / Mind Map",
        "briefing": "执行简报 / Briefing Doc",
        "study_guide": "学习指南 / Study Guide",
        "faq": "常见问题 / FAQ",
        "timeline": "时间线 / Timeline",
        "quiz": "互动测验 / Quiz",
        "flashcards": "抽认卡 / Flashcards",
        "presentation": "演示文稿 / Presentation"
    }
    title = f"{titles_map.get(req.artifact_type, 'Artifact')} ({datetime.datetime.now().strftime('%m-%d %H:%M')})"

    artifact_result = await generate_studio_artifact(
        artifact_type=req.artifact_type,
        sources_context=sources_context,
        language=req.language
    )

    artifact_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO studio_artifacts (id, notebook_id, artifact_type, title, content_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (artifact_id, req.notebook_id, req.artifact_type, title, json.dumps(artifact_result), now))

    conn.commit()
    conn.close()

    return {
        "id": artifact_id,
        "title": title,
        "artifact_type": req.artifact_type,
        "content": artifact_result,
        "created_at": now
    }

@router.get("/download/{filename}")
def download_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@router.delete("/{artifact_id}")
def delete_artifact(artifact_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM studio_artifacts WHERE id = ?", (artifact_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": artifact_id}
