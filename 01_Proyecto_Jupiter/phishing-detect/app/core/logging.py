from __future__ import annotations

import json
import logging
import os
import sys
import time
import traceback
from contextvars import ContextVar
from typing import Any, Dict
import logging.handlers

# Contexto por request (se propaga a cualquier log dentro del request)
trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="-")
user_id_ctx: ContextVar[str] = ContextVar("user_id", default="-")
session_id_ctx: ContextVar[str] = ContextVar("session_id", default="-")


class JsonFormatter(logging.Formatter):
    """
    Formatter JSON: cada log = una línea JSON.
    Incluye contexto (trace_id, user_id, session_id) y campos extra.
    """

    def format(self, record: logging.LogRecord) -> str:
        base: Dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", trace_id_ctx.get()),
            "user_id": getattr(record, "user_id", user_id_ctx.get()),
            "session_id": getattr(record, "session_id", session_id_ctx.get()),
        }

        # Campos estándar opcionales
        if hasattr(record, "event"):
            base["event"] = getattr(record, "event")
        if hasattr(record, "path"):
            base["path"] = getattr(record, "path")
        if hasattr(record, "method"):
            base["method"] = getattr(record, "method")
        if hasattr(record, "status_code"):
            base["status_code"] = getattr(record, "status_code")
        if hasattr(record, "duration_ms"):
            base["duration_ms"] = getattr(record, "duration_ms")

        # Extra payload (dict)
        extra_payload = getattr(record, "extra", None)
        if isinstance(extra_payload, dict):
            base.update(extra_payload)

        # Excepción (si existe)
        if record.exc_info:
            base["error"] = {
                "type": str(record.exc_info[0].__name__) if record.exc_info[0] else "Exception",
                "message": str(record.exc_info[1]) if record.exc_info[1] else "",
                "stack": "".join(traceback.format_exception(*record.exc_info))[-4000:],  # selecciona los ultimos 4000
            }

        return json.dumps(base, ensure_ascii=False)


class ContextFilter(logging.Filter):
    """Inyecta contexto actual (trace_id, user_id, session_id) en cada record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = trace_id_ctx.get()
        record.user_id = user_id_ctx.get()
        record.session_id = session_id_ctx.get()
        return True


def setup_logging(app_name: str = "phishing-chat", log_file: str = "") -> None:
    """
    Configura logging global (root) con salida JSON.

    Args:
        app_name(str): Nombre de la aplicacion
        log_file(str): Ruta de los archivos logs
    """
    level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # Evitar duplicados si uvicorn recarga
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(ContextFilter())
    root.addHandler(handler)

    # Archivo logs opcional si está LOG_FILE en el archivo .env
    log_file = log_file.strip()
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(JsonFormatter())
        file_handler.addFilter(ContextFilter())
        root.addHandler(file_handler)

    # Ajustes para verbosidad de librerías
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.WARNING)
    logging.getLogger("celery.app.trace").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("dns").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("langchain_core").setLevel(logging.WARNING)
    logging.getLogger("langchain_community").setLevel(logging.WARNING)
    logging.getLogger("langchain_google_genai").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)
    logging.getLogger("qdrant_client").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(
    logger: logging.Logger,
    *,
    level: int,
    event: str,
    message: str,
    trace_id: str | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
    extra: dict[str, Any] | None = None,
    exc_info: bool = False,
) -> None:
    """
    Logging estructurado uniforme.
    """
    payload: dict[str, Any] = {
        "event": event,
        "extra": extra or {},
    }
    if trace_id is not None:
        payload["trace_id"] = trace_id
    if user_id is not None:
        payload["user_id"] = user_id
    if session_id is not None:
        payload["session_id"] = session_id

    logger.log(level, message, extra=payload, exc_info=exc_info)
