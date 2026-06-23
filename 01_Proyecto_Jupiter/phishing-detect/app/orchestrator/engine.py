from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.core.logging import get_logger, log_event
from app.core.settings import settings
from app.orchestrator.cu02.handler import handle_cu02
from app.orchestrator.cu03.handler import handle_cu03
from app.orchestrator.cu04.handler import handle_cu04
from app.orchestrator.router import (
    OPTION_CREATE_ALERT,
    OPTION_CREATE_DOMAIN,
    OPTION_LOOKUP_DOMAIN,
    OPTION_RAG_QUERY,
    OPTION_UNKNOWN,
    RouteDecision,
    build_menu_message,
    route_message,
)
from app.orchestrator.cu01.handler import handle_cu01
from app.storage.rule_draft_store import get_rule_draft
from app.storage.domain_draft_store import get_domain_draft
from app.storage.analysis_draft_store import get_analysis_draft
from app.storage.rag_draft_store import get_rag_draft

logger = get_logger("orchestrator.engine")

_CANCEL_WORDS = {"cancelar", "cancela", "salir", "volver", "menu", "menú", "inicio"}

_openai_client = OpenAI(api_key=settings.openai_api_key, timeout=30.0, max_retries=1)


def run_orchestrator(user_id: str, session_id: str, message: str, model: str) -> dict[str, Any]:
    """
    Orquestador principal del chat.

    Si hay una sesión activa (CU-01 a CU-04), enruta el mensaje directamente
    al handler correspondiente sin pasar por el router. Si no hay sesión activa,
    usa el router para clasificar el mensaje y despachar al CU apropiado.
    """
    # Comprobamos si hay algun borrador activo para el usuario y sesión
    draft_entry = get_rule_draft(user_id=user_id, session_id=session_id)
    draft = (draft_entry or {}).get("draft", {}) if isinstance(draft_entry, dict) else {}

    domain_draft_entry = get_domain_draft(user_id=user_id, session_id=session_id)
    domain_draft = (domain_draft_entry or {}).get("draft", {}) if isinstance(domain_draft_entry, dict) else {}

    analysis_draft_entry = get_analysis_draft(user_id=user_id, session_id=session_id)
    analysis_draft = (analysis_draft_entry or {}).get("draft", {}) if isinstance(analysis_draft_entry, dict) else {}

    rag_draft_entry = get_rag_draft(user_id=user_id, session_id=session_id)
    rag_draft = (rag_draft_entry or {}).get("draft", {}) if isinstance(rag_draft_entry, dict) else {}

    in_cu03_flow = (
        draft.get("_active_cu") == "CU-03"
        or bool(draft.get("_pending_fields"))
        or bool(draft.get("_awaiting_confirmation"))
        or bool(draft.get("_awaiting_domain_register_confirm"))
        or draft.get("_action") in ("delete", "toggle")
    )

    in_cu02_flow = (
        domain_draft.get("_active_cu") == "CU-02"
        or bool(domain_draft.get("_awaiting_tags"))
        or bool(domain_draft.get("_awaiting_confirmation"))
    )

    in_cu01_flow = (
        analysis_draft.get("_active_cu") == "CU-01"
        or bool(analysis_draft.get("_awaiting_url"))
    )

    in_cu04_flow = (
        rag_draft.get("_active_cu") == "CU-04"
        or bool(rag_draft.get("_awaiting_question"))
    )

    if in_cu03_flow:
        decision = RouteDecision(
            option=OPTION_CREATE_ALERT,
            confidence=1.0,
            reason="sticky_cu03_session",
        )
    elif in_cu02_flow:
        decision = RouteDecision(
            option=OPTION_CREATE_DOMAIN,
            confidence=1.0,
            reason="sticky_cu02_session",
        )
    elif in_cu01_flow:
        decision = RouteDecision(
            option=OPTION_LOOKUP_DOMAIN,
            confidence=1.0,
            reason="sticky_cu01_session",
        )
    elif in_cu04_flow:
        decision = RouteDecision(
            option=OPTION_RAG_QUERY,
            confidence=1.0,
            reason="sticky_cu04_session"
        )
    else:
        decision = route_message(text=message, model=model, client=_openai_client)

    log_event(
        logger,
        level=20,
        event="orchestrator_start",
        message="Inicia el orquestador",
        extra={"model": model, "option": decision.option},
    )

    log_event(
        logger,
        level=20,
        event="router_decision",
        message="Decision de routing",
        extra={
            "option": decision.option,
            "confidence": decision.confidence,
            "reason": decision.reason,
        },
    )

    if decision.option == OPTION_CREATE_ALERT:
        result = handle_cu03(
            user_id=user_id,
            session_id=session_id,
            message=message,
            model=model,
            client=_openai_client,
        )
        result.setdefault("show_menu", False)
    elif decision.option == OPTION_LOOKUP_DOMAIN:
        result = handle_cu01(
            user_id=user_id,
            session_id=session_id,
            message=message,
            model=model,
            client=_openai_client,
        )
        result.setdefault("show_menu", False)
    elif decision.option == OPTION_CREATE_DOMAIN:
        result = handle_cu02(
            user_id=user_id,
            session_id=session_id,
            message=message,
            model=model,
            client=_openai_client,
        )
        result.setdefault("show_menu", False)
    elif decision.option == OPTION_RAG_QUERY:
        result = handle_cu04(
            user_id=user_id,
            session_id=session_id,
            message=message,
        )
        result.setdefault("show_menu", False)
    else:
        _CANCEL_WORDS = {"cancelar", "cancela", "salir", "volver", "menu", "menú", "inicio"}
        normalized_msg = " ".join(message.strip().lower().split())
        if normalized_msg in _CANCEL_WORDS or "volver al menu" in normalized_msg:
            msg = "Ya estás en el menú principal. Selecciona una opción."
        else:
            msg = "No he entendido la opcion solicitada. Selecciona una de las opciones del menu."
        result = {
            "final_user_message": build_menu_message(msg),
            "option": OPTION_UNKNOWN,
            "show_menu": True,
        }

    log_event(
        logger,
        level=20,
        event="orchestrator_end",
        message="Finalizado el orquestador",
        extra={"option": decision.option},
    )

    return result
