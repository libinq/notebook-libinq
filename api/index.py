"""Vercel serverless entrypoint.

Exposes the existing FastAPI application (backend/app/main.py) as an ASGI
handler so that Vercel's Python runtime can serve both the REST API and the
static frontend from a single deployment.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app  # noqa: E402,F401
