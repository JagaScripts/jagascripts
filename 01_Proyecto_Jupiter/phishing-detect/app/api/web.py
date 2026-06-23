from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

# app/api/web.py  -> subimos dos niveles -> app/ -> web/index.html
WEB_DIR = Path(__file__).resolve().parents[1] / "web"
INDEX_FILE = WEB_DIR / "index.html"


@router.get("/", response_class=HTMLResponse)
def serve_index() -> HTMLResponse:
    html = INDEX_FILE.read_text(encoding="utf-8")
    return HTMLResponse(content=html)
