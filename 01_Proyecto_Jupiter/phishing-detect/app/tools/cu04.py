from __future__ import annotations

from app.core.logging import get_logger, log_event
from app.services.rag_service import rag_service

logger = get_logger("tools.cu04")


def ask_rag(question: str) -> dict[str, object]:
    """Consulta el sistema RAG con una pregunta sobre phishing

    Args:
        question: Pregunta del usuario

    Returns:
        dict [str, object] con 'answer' y 'sources'
        En caso de error, devuelve dict con 'error'
    """
    if not question.strip():
        return {"error": "La pregunta no puede estar vacía."}

    try:
        return rag_service.ask(question)
    except ValueError as exc:
        msg = str(exc)
        if "Collection not found" in msg or "colección" in msg.lower():
            log_event(
                logger,
                level=30,
                event="rag_collection_missing",
                message="Consulta RAG sin colección indexada",
            )
            return {
                "error": (
                    "La base de conocimiento RAG no está disponible todavía. "
                    "Es posible que la ingesta esté en curso o que haya fallado al arrancar. "
                    "Revisa los logs de la aplicación."
                )
            }
        log_event(
            logger,
            level=40,
            event="rag_ask_error",
            message="Error en consulta RAG",
            extra={"error": msg},
        )
        return {"error": f"Error al consultar la base de conocimiento: {msg}"}
    except Exception as exc:
        log_event(
            logger,
            level=40,
            event="rag_ask_unexpected_error",
            message="Error inesperado en consulta RAG",
            extra={"error": str(exc)},
        )
        return {"error": "Error inesperado al consultar la base de conocimiento RAG."}
