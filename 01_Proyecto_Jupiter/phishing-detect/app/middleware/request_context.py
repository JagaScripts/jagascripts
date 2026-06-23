from __future__ import annotations
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from app.core.logging import trace_id_ctx, user_id_ctx, session_id_ctx, get_logger, log_event
from app.storage.audit_store import write_audit_event

logger = get_logger("middleware.request")


async def request_context_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware que asigna un trace_id por petición, extrae user_id/session_id si están presentes,
    registra logs y eventos de auditoría, y mide la duración de la solicitud.

    Args:
        request (Request): Objeto de la petición HTTP entrante.
        call_next (Callable): Función que continúa el procesamiento de la petición.

    Returns:
        Response: Respuesta HTTP generada por la aplicación.
    """

    trace_id = request.headers.get("X-Trace-Id") or f"tr_{uuid.uuid4().hex[:12]}"
    trace_id_ctx.set(trace_id)

    # Defaults de contexto
    user_id_ctx.set("-")
    session_id_ctx.set("-")

    # Intento no intrusivo de extraer user_id/session_id si el body es JSON
    try:
        if request.headers.get("content-type", "").startswith("application/json"):
            body = await request.json()
            if isinstance(body, dict):
                if "user_id" in body:
                    user_id_ctx.set(str(body.get("user_id") or "-"))
                if "session_id" in body and body.get("session_id"):
                    session_id_ctx.set(str(body.get("session_id")))
    except Exception:
        pass

    start = time.time()

    log_event(
        logger,
        level=20,
        event="http_request_start",
        message="Request start",
        extra={"method": request.method, "path": request.url.path},
    )

    write_audit_event(
        trace_id=trace_id_ctx.get(),
        user_id=user_id_ctx.get(),
        session_id=session_id_ctx.get(),
        event="http_request_start",
        payload={
            "method": request.method,
            "path": request.url.path,
        },
    )

    try:
        response: Response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)

        log_event(
            logger,
            level=20,
            event="http_request_end",
            message="Request end",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id_ctx.get(),
            session_id=session_id_ctx.get(),
            event="http_request_end",
            payload={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        # Propaga trace_id al cliente
        response.headers["X-Trace-Id"] = trace_id
        return response

    except Exception:
        duration_ms = int((time.time() - start) * 1000)

        log_event(
            logger,
            level=40,
            event="http_request_error",
            message="Request error",
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
            },
            exc_info=True,
        )

        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id_ctx.get(),
            session_id=session_id_ctx.get(),
            event="http_request_error",
            payload={
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
            },
        )

        raise
