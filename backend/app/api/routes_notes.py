import uuid
import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..db import get_connection
from .routes_sources import save_source_and_chunks

router = APIRouter(prefix="/api/notes", tags=["notes"])

class NoteCreate(BaseModel):
    notebook_id: str
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: str
    content: str

@router.get("")
def list_notes(notebook_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM notes 
        WHERE notebook_id = ? 
        ORDER BY updated_at DESC
    """, (notebook_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"notes": rows}

@router.post("")
def create_note(req: NoteCreate):
    note_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notes (id, notebook_id, title, content, is_source, created_at, updated_at)
        VALUES (?, ?, ?, ?, 0, ?, ?)
    """, (note_id, req.notebook_id, req.title.strip() or "Untitled Note", req.content.strip(), now, now))
    conn.commit()
    conn.close()
    return {"id": note_id, "title": req.title, "content": req.content, "is_source": 0, "created_at": now}

@router.put("/{note_id}")
def update_note(note_id: str, req: NoteUpdate):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notes SET title = ?, content = ?, updated_at = ?
        WHERE id = ?
    """, (req.title.strip(), req.content.strip(), now, note_id))
    conn.commit()
    conn.close()
    return {"status": "updated", "id": note_id}

@router.delete("/{note_id}")
def delete_note(note_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": note_id}

@router.post("/{note_id}/promote")
def promote_note_to_source(note_id: str):
    """
    Promote an insight note into a knowledge source so it feeds back into RAG!
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Note not found")

    note = dict(row)
    # Mark note as promoted
    cursor.execute("UPDATE notes SET is_source = 1 WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

    source = save_source_and_chunks(
        notebook_id=note["notebook_id"],
        title=f"[笔记] {note['title']}",
        source_type="note",
        content=note["content"]
    )

    return {"status": "promoted", "source": source}
