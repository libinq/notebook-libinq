import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Serverless platforms (e.g. Vercel) only allow writes to /tmp, and the
# bundled source directory is read-only at runtime.
if os.getenv("VERCEL"):
    DATA_DIR = Path("/tmp/data")
else:
    DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
AUDIO_DIR = DATA_DIR / "audio"
DB_PATH = DATA_DIR / "notebook.db"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Default LLM configuration
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "deepseek")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "deepseek-chat")
DEFAULT_BASE_URL = os.getenv("DEFAULT_BASE_URL", "https://api.deepseek.com/v1")
DEFAULT_API_KEY = os.getenv("DEFAULT_API_KEY", "")

# Server configuration
PORT = int(os.getenv("PORT", "8502"))
HOST = os.getenv("HOST", "0.0.0.0")
