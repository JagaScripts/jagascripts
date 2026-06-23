from __future__ import annotations

from typing import Any

from app.core.logging import get_logger, log_event
from app.orchestrator.cu04.extractors import extract_question
from app.orchestrator.cu04.questions import ask_for_question
from app.orchestrator.router import build_menu_message
from app.storage.rag_draft_store import (
    clear_rag_draft,
    get_rag_draft,
    upsert_rag_draft,
)
from app.tools.cu04 import ask_rag

logger = get_logger("cu04.handler")


def _normalize_text(text: str) -> str:
    """ Cambia el texto a minúsculas y elimina espacios"""
    return " ".join((text or "").strip().lower().split())


def _wants_exit(text: str) -> bool:
    """
    Verifica si la intención del usuario es volver al menú principal o cancelar

    Args:
        text(str): Mesaje del usuario

    Returns:
        bool: True si el usuario quiere cancelar o volver al menu principal
    """
    text = _normalize_text(text)
    exit_commands = {
        "cancelar",
        "cancela",
        "salir",
        "salir del flujo",
        "abortar",
        "parar",
        "menu",
        "menú",
        "inicio",
        "volver",
        "volver al menu",
        "volver al menú",
    }
    return text in exit_commands or "volver al menu" in text


def handle_cu04(
    user_id: str,
    session_id: str,
    message: str,
) -> dict[str, Any]:
    """Gestiona el flujo conversacional para consultas RAG sobre phishing.

    Si el usuario seleccionó la opción sin incluir pregunta, la solicita.
    Si hay pregunta, consulta la base de conocimiento y devuelve la respuesta.
    No usa OpenAI: el LLM es Gemini a través de rag_service.

    Args:
        user_id(str): Identificador del usuario
        session_id(str): Identificador de la sesión
        message(str): Último mensaje del usuario

    Returns:
        dict[str, Any]: Respuesta con final_user_message y flags de control
    """
    draft_entry = get_rag_draft(user_id=user_id, session_id=session_id)
    draft = draft_entry.get("draft", {}) or {}

    if not draft:
        log_event(
            logger,
            level=20,
            event="cu04_flow_started",
            message=f"CU-04 iniciado por usuario {user_id}",
            session_id=session_id,
            user_id=user_id,
        )

    if _wants_exit(message):
        clear_rag_draft(user_id=user_id, session_id=session_id)
        log_event(
            logger,
            level=20,
            event="cu04_flow_cancelled",
            message=f"CU-04 cancelado por usuario {user_id}",
            session_id=session_id,
            user_id=user_id,
        )
        return {
            "final_user_message": build_menu_message("Consulta cancelada. Puedes elegir otra opción."),
            "cu": "CU-04",
            "show_menu": True,
        }

    question = extract_question(message)

    if not question:
        upsert_rag_draft(
            user_id=user_id,
            session_id=session_id,
            patch={"_active_cu": "CU-04", "_awaiting_question": True},
        )
        return {
            "final_user_message": ask_for_question(),
            "cu": "CU-04",
            "show_menu": False,
        }

    clear_rag_draft(user_id=user_id, session_id=session_id)

    log_event(
        logger,
        level=20,
        event="cu04_question_received",
        message=f"Consulta RAG de usuario {user_id}",
        session_id=session_id,
        user_id=user_id,
        extra={"question": question[:100]},
    )

    result = ask_rag(question)

    if result.get("error"):
        return {
            "final_user_message": build_menu_message(str(result["error"])),
            "cu": "CU-04",
            "show_menu": True,
        }

    log_event(
        logger,
        level=20,
        event="cu04_answer_delivered",
        message=f"Respuesta RAG entregada a usuario {user_id}",
        session_id=session_id,
        user_id=user_id,
        extra={"sources_count": len(result.get("sources", []))},
    )

    upsert_rag_draft(
        user_id=user_id,
        session_id=session_id,
        patch={"_active_cu": "CU-04", "_awaiting_question": True},
    )

    return {
        "final_user_message": str(result["answer"]) + "\n\n_¿Tienes alguna otra pregunta? Escribe **cancelar** para volver al menú._",  # noqa: E501
        "cu": "CU-04",
        "show_menu": False,
    }
