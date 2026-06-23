from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from app.db.models import AuditLog
from app.db.session import SessionLocal

_AUDIT_ENABLED = os.getenv("AUDIT_ENABLED", "true").lower() in ("1", "true", "yes", "y")


def init_audit_db() -> None:
    """
    No-op: la tabla audit_log se crea con create_all() en el arranque de la app.
    Se mantiene la firma para compatibilidad con main.py.
    """
    pass


def write_audit_event(
    *,
    trace_id: str,
    event: str,
    payload: dict[str, Any],
    user_id: str | None = None,
    session_id: str | None = None,
) -> None:
    """
    Registra un evento de auditoría en PostgreSQL.

    Args:
        trace_id(str): Identificador de traza de la petición
        event(str): Nombre del evento
        payload(dict[str, Any]): Datos adicionales del evento
        user_id(str | None): Identificador del usuario
        session_id(str | None): Identificador de la sesión
    """

    if not _AUDIT_ENABLED:
        return

    ts_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    db = SessionLocal()
    try:
        db.add(AuditLog(
            ts_utc=ts_utc,
            trace_id=trace_id,
            user_id=user_id,
            session_id=session_id,
            event=event,
            payload_json=payload,
        ))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def read_audit_session(session_id: str, limit: int = 200) -> list[dict[str, Any]]:
    """
    Recupera los eventos de auditoría asociados a un session_id

    Args:
        session_id (str): Identificador de sesion.
        limit (int): Número máximo de registros a devolver (por defecto 200).

    Returns:
        list[dict[str, Any]]: Lista de eventos de auditoría ordenados cronológicamente.
    """

    if not _AUDIT_ENABLED:
        return []

    db = SessionLocal()
    try:
        rows = (
            db.query(AuditLog)
            .filter(AuditLog.session_id == session_id)
            .order_by(AuditLog.id.asc())
            .limit(limit)
            .all()
        )
        return [
            {
                "ts_utc": r.ts_utc,
                "trace_id": r.trace_id,
                "user_id": r.user_id,
                "session_id": r.session_id,
                "event": r.event,
                "payload": r.payload_json,
            }
            for r in rows
        ]
    except Exception:
        return []
    finally:
        db.close()
