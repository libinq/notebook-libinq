import json
import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..db import get_connection
from ..retrieval.bm25 import BM25Retriever
from ..llm.prompts import CHAT_GROUNDING_PROMPT
from ..llm.provider import stream_llm

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    notebook_id: str
    message: str
    source_ids: Optional[List[str]] = None

@router.get("/history")
def get_chat_history(notebook_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM chat_messages 
        WHERE notebook_id = ? 
        ORDER BY created_at ASC
    """, (notebook_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    for r in rows:
        try:
            r["citations"] = json.loads(r.get("citations_json", "[]"))
        except Exception:
            r["citations"] = []
    conn.close()
    return {"messages": rows}

@router.delete("/history")
def clear_chat_history(notebook_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_messages WHERE notebook_id = ?", (notebook_id,))
    conn.commit()
    conn.close()
    return {"status": "cleared"}

@router.post("/stream")
async def chat_stream(req: ChatRequest):
    user_query = req.message.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Query message cannot be empty")

    conn = get_connection()
    cursor = conn.cursor()

    # Retrieve selected sources or all sources in notebook
    if req.source_ids and len(req.source_ids) > 0:
        placeholders = ",".join(["?"] * len(req.source_ids))
        cursor.execute(f"SELECT * FROM sources WHERE id IN ({placeholders})", req.source_ids)
    else:
        cursor.execute("SELECT * FROM sources WHERE notebook_id = ?", (req.notebook_id,))
    
    sources = [dict(r) for r in cursor.fetchall()]

    # If no sources, return informative message
    if not sources:
        conn.close()
        async def no_source_gen():
            msg = "当前笔记本尚未添加任何来源资料。请先在左侧上传文档（PDF、Word、PPT、Excel）、网页链接或粘贴文本，然后即可开展知识对话与引用溯源！"
            yield f"data: {json.dumps({'type': 'citations', 'citations': []})}\n\n"
            yield f"data: {json.dumps({'type': 'token', 'token': msg})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(no_source_gen(), media_type="text/event-stream")

    # Fetch chunks for the chosen sources
    source_ids = [s["id"] for s in sources]
    placeholders = ",".join(["?"] * len(source_ids))
    cursor.execute(f"""
        SELECT c.*, s.title as source_title 
        FROM source_chunks c 
        JOIN sources s ON c.source_id = s.id 
        WHERE c.source_id IN ({placeholders})
        ORDER BY c.source_id, c.chunk_index ASC
    """, source_ids)
    all_chunks = [dict(r) for r in cursor.fetchall()]

    total_chars = sum(len(c["content"]) for c in all_chunks)
    
    # Strategy: if <= 100k chars, use full source context; else BM25 top 24
    if total_chars <= 100000:
        selected_chunks = all_chunks
    else:
        retriever = BM25Retriever()
        retriever.index(all_chunks)
        selected_chunks = retriever.search(user_query, top_k=24)

    # Build citation registry and context text
    citations_meta = []
    context_lines = []
    
    for idx, chunk in enumerate(selected_chunks):
        cite_num = idx + 1
        source_title = chunk.get("source_title", "Unknown Source")
        content = chunk.get("content", "").strip()
        citations_meta.append({
            "citation_index": cite_num,
            "source_id": chunk["source_id"],
            "chunk_index": chunk["chunk_index"],
            "source_title": source_title,
            "snippet": content[:200] + ("..." if len(content) > 200 else "")
        })
        context_lines.append(f"--- [Source {cite_num}]: {source_title} ---\n{content}")

    sources_context = "\n\n".join(context_lines)

    # Build conversation messages
    system_instruction = CHAT_GROUNDING_PROMPT.format(sources_context=sources_context)
    
    # Pull recent chat history (last 6 messages) for conversational context
    cursor.execute("""
        SELECT role, content FROM chat_messages 
        WHERE notebook_id = ? 
        ORDER BY created_at DESC LIMIT 6
    """, (req.notebook_id,))
    history_rows = cursor.fetchall()
    history = [dict(r) for r in reversed(history_rows)]

    messages = [{"role": "system", "content": system_instruction}]
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_query})

    # Save user message
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cursor.execute(
        "INSERT INTO chat_messages (id, notebook_id, role, content, citations_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), req.notebook_id, "user", user_query, "[]", now)
    )
    conn.commit()
    conn.close()

    async def event_generator():
        # First send citation metadata so frontend can immediately register citation popovers
        yield f"data: {json.dumps({'type': 'citations', 'citations': citations_meta})}\n\n"
        
        full_assistant_reply = []
        async for token in stream_llm(messages, temperature=0.3):
            full_assistant_reply.append(token)
            yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"

        complete_text = "".join(full_assistant_reply)
        
        # Save assistant message to DB
        save_conn = get_connection()
        save_cursor = save_conn.cursor()
        save_now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save_cursor.execute(
            "INSERT INTO chat_messages (id, notebook_id, role, content, citations_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), req.notebook_id, "assistant", complete_text, json.dumps(citations_meta), save_now)
        )
        save_conn.commit()
        save_conn.close()

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
