import uuid
import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from ..db import get_connection

router = APIRouter(prefix="/api/notebooks", tags=["notebooks"])

class NotebookCreate(BaseModel):
    title: str
    description: Optional[str] = ""

class NotebookUpdate(BaseModel):
    title: str
    description: Optional[str] = ""

@router.get("")
def list_notebooks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.*, 
               (SELECT COUNT(*) FROM sources WHERE notebook_id = n.id) as source_count,
               (SELECT COUNT(*) FROM notes WHERE notebook_id = n.id) as note_count
        FROM notebooks n ORDER BY n.updated_at DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"notebooks": rows}

@router.post("")
def create_notebook(req: NotebookCreate):
    notebook_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notebooks (id, title, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (notebook_id, req.title.strip() or "Untitled Notebook", req.description, now, now)
    )
    conn.commit()
    conn.close()
    return {"id": notebook_id, "title": req.title, "description": req.description, "created_at": now}

@router.delete("/{notebook_id}")
def delete_notebook(notebook_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notebooks WHERE id = ?", (notebook_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": notebook_id}

@router.put("/{notebook_id}")
def update_notebook(notebook_id: str, req: NotebookUpdate):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE notebooks SET title = ?, description = ?, updated_at = ? WHERE id = ?",
        (req.title.strip(), req.description, now, notebook_id)
    )
    conn.commit()
    conn.close()
    return {"status": "updated", "id": notebook_id}
