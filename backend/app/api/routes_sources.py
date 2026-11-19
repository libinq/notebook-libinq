import uuid
import datetime
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from ..db import get_connection
from ..config import UPLOAD_DIR
from ..ingestion.parser import extract_text_from_file, chunk_document
from ..ingestion.web_reader import extract_web_content
from ..ingestion.youtube import fetch_youtube_transcript

router = APIRouter(prefix="/api/sources", tags=["sources"])

class URLSourceCreate(BaseModel):
    notebook_id: str
    url: str

class TextSourceCreate(BaseModel):
    notebook_id: str
    title: str
    content: str

def save_source_and_chunks(notebook_id: str, title: str, source_type: str, content: str, file_path: str = "") -> dict:
    source_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    char_count = len(content)
    
    # Generate summary preview
    summary = content[:280] + ("..." if len(content) > 280 else "")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sources (id, notebook_id, title, source_type, file_path, content, summary, char_count, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (source_id, notebook_id, title, source_type, file_path, content, summary, char_count, now))

    # Chunk content
    chunks = chunk_document(content)
    for c in chunks:
        chunk_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO source_chunks (id, source_id, notebook_id, chunk_index, content, char_offset)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chunk_id, source_id, notebook_id, c["chunk_index"], c["content"], c["char_offset"]))

    # Update notebook timestamp
    cursor.execute("UPDATE notebooks SET updated_at = ? WHERE id = ?", (now, notebook_id))

    conn.commit()
    conn.close()

    return {
        "id": source_id,
        "notebook_id": notebook_id,
        "title": title,
        "source_type": source_type,
        "summary": summary,
        "char_count": char_count,
        "chunks_count": len(chunks),
        "created_at": now
    }

@router.get("")
def list_sources(notebook_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, notebook_id, title, source_type, summary, char_count, created_at,
               (SELECT COUNT(*) FROM source_chunks WHERE source_id = s.id) as chunk_count
        FROM sources s WHERE notebook_id = ? ORDER BY created_at DESC
    """, (notebook_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"sources": rows}

@router.get("/{source_id}")
def get_source_detail(source_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sources WHERE id = ?", (source_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Source not found")
    
    source = dict(row)
    cursor.execute("SELECT * FROM source_chunks WHERE source_id = ? ORDER BY chunk_index ASC", (source_id,))
    source["chunks"] = [dict(c) for c in cursor.fetchall()]
    conn.close()
    return source

@router.post("/upload")
async def upload_file(notebook_id: str = Form(...), file: UploadFile = File(...)):
    filename = file.filename or "upload"
    file_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{file_id}_{filename}"
    
    with open(save_path, "wb") as f:
        f.write(await file.read())

    try:
        content = extract_text_from_file(save_path)
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")

    if not content.strip():
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="The uploaded document contains no extractable text.")

    res = save_source_and_chunks(notebook_id, filename, "file", content, str(save_path))
    return res

@router.post("/url")
async def add_url(req: URLSourceCreate):
    url = req.url.strip()
    if "youtube.com" in url or "youtu.be" in url:
        title, content = fetch_youtube_transcript(url)
        source_type = "youtube"
    else:
        try:
            title, content = extract_web_content(url)
            source_type = "url"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch webpage: {str(e)}")

    if not content.strip():
        raise HTTPException(status_code=400, detail="Could not extract readable content from URL.")

    res = save_source_and_chunks(req.notebook_id, title, source_type, content, url)
    return res

@router.post("/text")
async def add_text(req: TextSourceCreate):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Text content cannot be empty.")
    
    title = req.title.strip() or req.content[:30] + "..."
    res = save_source_and_chunks(req.notebook_id, title, "text", req.content.strip())
    return res

@router.delete("/{source_id}")
def delete_source(source_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM sources WHERE id = ?", (source_id,))
    row = cursor.fetchone()
    if row and row["file_path"] and Path(row["file_path"]).exists():
        try:
            Path(row["file_path"]).unlink()
        except Exception:
            pass
            
    cursor.execute("DELETE FROM source_chunks WHERE source_id = ?", (source_id,))
    cursor.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": source_id}
