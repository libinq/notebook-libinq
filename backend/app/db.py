import sqlite3
import json
import uuid
import datetime
from typing import List, Dict, Any, Optional
from .config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Notebooks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notebooks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    # 2. Sources
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sources (
        id TEXT PRIMARY KEY,
        notebook_id TEXT NOT NULL,
        title TEXT NOT NULL,
        source_type TEXT NOT NULL,
        file_path TEXT DEFAULT '',
        content TEXT NOT NULL,
        summary TEXT DEFAULT '',
        char_count INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
    )
    """)
    
    # 3. Source Chunks for Citation and Retrieval
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS source_chunks (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        notebook_id TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        content TEXT NOT NULL,
        char_offset INTEGER DEFAULT 0,
        FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE CASCADE
    )
    """)
    
    # 4. Notes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id TEXT PRIMARY KEY,
        notebook_id TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        is_source INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
    )
    """)
    
    # 5. Chat Messages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id TEXT PRIMARY KEY,
        notebook_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        citations_json TEXT DEFAULT '[]',
        created_at TEXT NOT NULL,
        FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
    )
    """)
    
    # 6. Podcasts (Audio Overview)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS podcasts (
        id TEXT PRIMARY KEY,
        notebook_id TEXT NOT NULL,
        title TEXT NOT NULL,
        format_type TEXT NOT NULL,
        language TEXT NOT NULL,
        duration_mode TEXT NOT NULL,
        audio_url TEXT DEFAULT '',
        script_json TEXT NOT NULL,
        status TEXT DEFAULT 'completed',
        created_at TEXT NOT NULL,
        FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
    )
    """)
    
    # 7. Studio Artifacts (MindMap, Briefing, Study Guide, FAQ, Timeline, Quiz, Flashcards, Presentation)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS studio_artifacts (
        id TEXT PRIMARY KEY,
        notebook_id TEXT NOT NULL,
        artifact_type TEXT NOT NULL,
        title TEXT NOT NULL,
        content_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
    )
    """)
    
    # 8. Settings (API keys, active providers, etc.)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)
    
    # Check if a default notebook exists; if not, create one
    cursor.execute("SELECT COUNT(*) FROM notebooks")
    if cursor.fetchone()[0] == 0:
        default_id = str(uuid.uuid4())
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cursor.execute(
            "INSERT INTO notebooks (id, title, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (default_id, "我的知识库 / My Knowledge Base", "默认笔记本 / Default Notebook", now, now)
        )
    
    conn.commit()
    conn.close()

# Helper queries
def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default

def set_setting(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

init_db()
