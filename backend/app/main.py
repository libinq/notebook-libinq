from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .db import init_db
from .config import BASE_DIR
from .api.routes_notebooks import router as notebooks_router
from .api.routes_sources import router as sources_router
from .api.routes_chat import router as chat_router
from .api.routes_podcast import router as podcast_router
from .api.routes_studio import router as studio_router
from .api.routes_notes import router as notes_router
from .api.routes_settings import router as settings_router

app = FastAPI(
    title="Open Notebook Bilingual",
    description="Privacy-focused, bilingual AI research & notebook studio benchmarking Google NotebookLM",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(notebooks_router)
app.include_router(sources_router)
app.include_router(chat_router)
app.include_router(podcast_router)
app.include_router(studio_router)
app.include_router(notes_router)
app.include_router(settings_router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "Open Notebook Bilingual"}

# Frontend static files
FRONTEND_DIR = BASE_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Open Notebook Bilingual Backend API is running."}
