from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.core.logging import get_logger, log_event
from app.db.session import SessionLocal
from app.orchestrator.cu01.extractors import regex_extract
from app.orchestrator.cu01.questions import ask_for_input
from app.orchestrator.router import build_menu_message
from app.storage.analysis_draft_store import (
    clear_analysis_draft,
    get_analysis_draft,
    upsert_analysis_draft,
)
from app.tools.cu01 import get_or_run_analysis

logger = get_logger("cu01.handler")

_RISK_LABEL = {
    "bajo": "BAJO",
    "medio": "MEDIO",
    "alto": "ALTO",
    "critico": "CRÍTICO",
}


def _normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _wants_exit(text: str) -> bool:
    """
    Detecta si el usuario quiere volver al menú principal

    Args:
        text(str): Mensaje del usuario

    Returns:
        bool: True si quiere cancelar o volver al menú
    """
    text = _normalize(text)
    exit_commands = {
        "cancelar", "cancela", "salir", "abortar", "parar",
        "menu", "menú", "inicio", "volver", "volver al menu", "volver al menú",
    }
    return text in exit_commands or "volver al menu" in text


def _format_result(result: dict[str, Any]) -> str:
    """
    Formatea el resultado del análisis para mostrar al usuario

    Args:
        result(dict[str, Any]): Resultado de get_or_run_analysis

    Returns:
        str: Mensaje formateado con score, nivel de riesgo y explicación
    """
    domain = result.get("domain", "-")
    score = result.get("score", 0)
    risk_level = _RISK_LABEL.get(result.get("risk_level", "bajo"), "BAJO")
    explanation = result.get("explanation", "")
    target = result.get("target_domain")
    target_sim = result.get("target_similarity")
    from_cache = result.get("from_cache", False)

    lines = [f"**Análisis de `{domain}`**\n"]
    lines.append(f"Nivel de riesgo: **{risk_level}** ({score}/100)\n")

    if target and target_sim:
        lines.append(f"Posible suplantación de: **{target}** (similitud {round(target_sim * 100)}%)\n")

    if explanation:
        lines.append(f"\n{explanation}")

    if from_cache:
        analyzed_at = result.get("analyzed_at", "")
        lines.append(f"\n_Resultado en caché (analizado: {analyzed_at[:10] if analyzed_at else 'recientemente'})_")

    return "\n".join(lines)


def handle_cu01(
    user_id: str,
    session_id: str,
    message: str,
    model: str,
    client: OpenAI,
) -> dict[str, Any]:
    """
    Gestiona el flujo conversacional para análisis de phishing

    Extrae URL/dominio/email del mensaje, ejecuta el análisis y devuelve
    el resultado con explicación generada por el LLM

    Args:
        user_id(str): Identificador del usuario
        session_id(str): Identificador de la sesión
        message(str): Último mensaje del usuario
        model(str): Modelo LLM a usar para la explicación
        client(OpenAI): Cliente OpenAI

    Returns:
        dict[str, Any]: Respuesta con final_user_message y flags de control
    """
    draft_entry = get_analysis_draft(user_id=user_id, session_id=session_id)
    draft = draft_entry.get("draft", {}) or {}

    if not draft:
        log_event(
            logger,
            level=20,
            event="cu01_flow_started",
            message=f"CU-01 iniciado por usuario {user_id}",
            session_id=session_id,
            user_id=user_id,
        )

    if _wants_exit(message):
        clear_analysis_draft(user_id=user_id, session_id=session_id)
        log_event(
            logger,
            level=20,
            event="cu01_flow_cancelled",
            message=f"CU-01 cancelado por usuario {user_id}",
            session_id=session_id,
            user_id=user_id,
        )
        return {
            "final_user_message": build_menu_message("Análisis cancelado. Puedes elegir otra opción."),
            "cu": "CU-01",
            "show_menu": True,
        }

    patch = regex_extract(message)
    raw_input = patch.get("raw_input")

    if not raw_input:
        # Si no ha detectado nada lo pide al usuario
        upsert_analysis_draft(
            user_id=user_id,
            session_id=session_id,
            patch={"_active_cu": "CU-01", "_awaiting_url": True},
        )
        return {
            "final_user_message": ask_for_input(),
            "cu": "CU-01",
            "show_menu": False,
        }

    clear_analysis_draft(user_id=user_id, session_id=session_id)

    try:
        with SessionLocal() as db:
            result = get_or_run_analysis(
                user_id=user_id,
                raw_input=raw_input,
                client=client,
                model=model,
                db=db,
            )
            db.commit()
    except Exception as e:
        logger.error(
            f"Error en análisis de phishing: {e}",
            extra={"event": "cu01_analysis_error", "error": str(e)},
            exc_info=True,
        )
        return {
            "final_user_message": build_menu_message(
                "Ha ocurrido un error al analizar el dominio. Inténtalo de nuevo."
            ),
            "cu": "CU-01",
            "show_menu": True,
        }

    if result.get("error"):
        return {
            "final_user_message": build_menu_message(
                f"No se pudo analizar el dominio: {result['error']}"
            ),
            "cu": "CU-01",
            "show_menu": True,
        }

    log_event(
        logger,
        level=20,
        event="cu01_analysis_complete",
        message=f"Análisis completado para {result.get('domain')}",
        session_id=session_id,
        user_id=user_id,
    )

    return {
        "final_user_message": _format_result(result),
        "cu": "CU-01",
        "show_menu": True,
    }
