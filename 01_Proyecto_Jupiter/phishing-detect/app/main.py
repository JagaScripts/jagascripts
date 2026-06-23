import atexit

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.orchestrator import router as orchestrator_router
from app.api.audit import router as audit_router
from app.api.web import router as web_router
from app.api.rules import router as rules_router

from app.core.logging import setup_logging, get_logger
from app.middleware.request_context import request_context_middleware
from app.storage.audit_store import init_audit_db
from app.db.init_db import init_db
from app.core.settings import settings
from app.sheduler import create_scheduler
from app.api.alerts import router as alerts_router
from app.data.tranco_loader import refresh_tranco_list
from app.services.rag_service import rag_service


def create_app() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI, inicializando logging, auditoría,
    base de datos, middleware y routers.

    Returns:
        FastAPI: Instancia de la aplicación configurada.
    """
    setup_logging(app_name="Phishing Detect", log_file=settings.log_file)
    logger = get_logger("app")

    init_audit_db()
    init_db()

    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Scheduler iniciado", extra={"event": "scheduler_started"})

    refresh_tranco_list()
    logger.info("Lista Tranco inicializada", extra={"event": "tranco_initialized"})

    app = FastAPI(title="Phishing Detect", version="0.1.0")
    app.middleware("http")(request_context_middleware)

    app.include_router(web_router, tags=["web"])
    app.include_router(health_router, prefix="/v1", tags=["health"])
    app.include_router(chat_router, prefix="/v1", tags=["chat"])
    app.include_router(orchestrator_router, prefix="/v1", tags=["orchestrator"])
    app.include_router(audit_router, prefix="/v1", tags=["audit"])
    app.include_router(rules_router, prefix="/v1", tags=["rules"])
    app.include_router(alerts_router, prefix="/v1", tags=["alerts"])

    # Al apagar la app, detener el scheduler sin esperar jobs en curso
    atexit.register(lambda: scheduler.shutdown(wait=False))

    logger.info("App creada", extra={"event": "app_start", "extra": {"version": "0.1.0"}})

    if settings.cu04_auto_ingest:
        try:
            rag_service.ingest()
        except Exception as exc:
            logger.warning(
                "RAG ingesta omitida al arrancar: %s", exc,
                extra={"event": "rag_ingest_startup_skipped"},
            )

    return app


app = create_app()
