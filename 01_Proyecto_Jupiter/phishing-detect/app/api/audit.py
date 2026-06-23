from __future__ import annotations
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from app.storage.audit_store import read_audit_session, write_audit_event
from app.core.logging import trace_id_ctx, user_id_ctx, session_id_ctx

router = APIRouter()


class AuditItem(BaseModel):
    """ Campos que va a tener cada elemento de la auditoría """
    ts_utc: int
    trace_id: str
    user_id: str | None = None
    session_id: str | None = None
    event: str
    payload: dict = Field(default_factory=dict)


class AuditResponse(BaseModel):
    """ Campos de respuesta cuando se requiere un elemento """
    session_id: str
    items: list[dict] = Field(default_factory=list)


@router.get("/audit/session/{session_id}", response_model=AuditResponse)
def get_audit_by_session(
    session_id: str,
    limit: int = Query(500, ge=1, le=2000),
) -> AuditResponse:
    """
    Obtiene el histórico completo de auditoría de una conversación (session_id).
    """
    items = read_audit_session(session_id=session_id, limit=limit)

    write_audit_event(
        trace_id=trace_id_ctx.get(),
        user_id=user_id_ctx.get(),
        session_id=session_id_ctx.get(),
        event="audit_log_queried",
        payload={"queried_session_id": session_id, "limit": limit, "results": len(items)},
    )

    return AuditResponse(
        session_id=f"session:{session_id}",
        items=items,
    )
