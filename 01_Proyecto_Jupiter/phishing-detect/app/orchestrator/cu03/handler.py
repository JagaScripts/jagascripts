from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.db.session import SessionLocal
from app.orchestrator.cu03.extractors import regex_extract, extract_cu03_crud_intent
from app.orchestrator.cu03.questions import build_question_for_missing, with_cancel_hint
from app.orchestrator.router import build_menu_message
from app.storage.rule_draft_store import clear_rule_draft, get_rule_draft, upsert_rule_draft
from app.tools.cu03 import (
    register_rule_schedule,
    resolve_scope,
    set_rule_targets,
    upsert_alert_rule,
    validate_alert_rule_dsl,
    list_alert_rules_tool,
    delete_alert_rule_tool,
    toggle_alert_rule_tool,
)
from app.tools.cu02 import register_domain as register_domain_cu02
from app.storage.audit_store import write_audit_event
from app.core.logging import trace_id_ctx, get_logger, log_event

logger = get_logger("cu03.handler")

_FIELD_ORDER = ["rule_type", "condition", "scope", "channels", "schedule", "rule_name"]


def _missing(draft: dict[str, Any]) -> list[str]:
    """
    Devuelve los campos obligatorios que faltan en el draft, ordenados por FIELD_ORDER

    Args:
        draft (dict): Estado actual del borrador

    Returns:
        list[str]: Campos pendientes de completar"""

    missing: list[str] = []

    if not draft.get("rule_name"):
        missing.append("rule_name")

    rule_type = draft.get("rule_type")
    if not rule_type:
        missing.append("rule_type")

    condition = draft.get("condition") or {}
    if rule_type == "expiry":
        if not condition.get("days_before_expiry"):
            missing.append("condition")
    else:
        if not condition:
            missing.append("condition")

    scope = draft.get("scope") or {}
    if not scope.get("domains") and not scope.get("domain_ids"):
        missing.append("scope")

    channels = draft.get("channels") or []
    has_email = any(
        isinstance(ch, dict) and ch.get("kind") == "email" and ch.get("to")
        for ch in channels
    )
    if not has_email:
        missing.append("channels")

    schedule = draft.get("schedule") or {}
    if not schedule.get("frequency"):
        missing.append("schedule")

    return [field for field in _FIELD_ORDER if field in missing]


def _normalize_text(text: str) -> str:
    """ Cambia el texto a minúsculas y elimina espacios"""
    return " ".join((text or "").strip().lower().split())


def _is_yes(text: str) -> bool:
    """
    Detecta si el mensaje del usuario es una confirmación afirmativa

    Args:
        text(str): Mensaje del usuario

    Returns:
        bool: True si el usuario confirma
    """
    text = _normalize_text(text)
    confirm_comands = {
        "si",
        "sí",
        "s",
        "ok",
        "vale",
        "confirmar",
        "confirmo",
        "crear",
        "crea",
        "adelante",
        "de acuerdo",
    }
    return text in confirm_comands or ("confirm" in text or "crea" in text)


def _is_no(text: str) -> bool:
    """
    Detecta si el mensaje del usuario es una negación o cancelación

    Args:
        text(str): Mensaje del usuario

    Returns:
        bool: True si el usuario cancela
    """
    text = _normalize_text(text)
    cancel_commands = {"no", "cancelar", "cancela", "anular", "anula", "parar"}
    return text in cancel_commands or ("cancel" in text or "anul" in text)


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


def _cancel_response() -> dict[str, Any]:
    """
    Crea la respuesta de cancelacion y muestra el menú principal

    Returns:
        dict[str, Any]: Datos para el mensaje de cancelacion y metadatos"""
    return {
        "final_user_message": build_menu_message(
            "Gestión de alertas cancelada. Puedes elegir otra opción."
        ),
        "cu": "CU-03",
        "show_menu": True,
    }


def _fallback_rule_name(message: str, draft: dict[str, Any]) -> str | None:
    """
    Extrae el nombre de regla del mensaje cuando el último campo preguntado fue rule_name
    y el extractor regex no encontró nada.

    Args:
        message (str): Mensaje del usuario.
        draft (dict): Estado actual del borrador.

    Returns:
        str | None: Nombre extraído o None si no aplica.
    """
    if draft.get("_last_question_field") != "rule_name":
        return None

    text = (message or "").strip().strip("\"'")
    if len(text) < 3 or len(text) > 80:
        return None

    lowered = text.lower()
    blocked_values = {
        "cancelar",
        "cancela",
        "salir",
        "menu",
        "menú",
        "si",
        "sí",
        "no",
    }
    if lowered in blocked_values:
        return None

    return text


def _format_rule_type(rule_type: str | None) -> str:
    """
    Traduce el tipo de regla ('expiry'/'risk') a texto en español
    De momento no se está implementando el tipo de alerta por riesgo
    """

    if rule_type == "expiry":
        return "caducidad"
    if rule_type == "risk":
        return "riesgo"
    return str(rule_type or "-")


def _format_condition(condition: dict[str, Any], rule_type: str | None) -> str:
    """
    Formatea la condición de la regla en texto legible según el tipo
    El tipo de regla por riesgo no se implementa de momento

    Args:
        condition(dict): Condición del borrador
        rule_type(str | None): Tipo de regla

    Returns:
        str: Texto descriptivo de la condición
    """
    if not condition:
        return "-"

    if rule_type == "expiry":
        days = condition.get("days_before_expiry") or condition.get("days_before")
        if days:
            return f"{days} dias antes de caducar"

    if rule_type == "risk":
        if condition.get("risk_level"):
            return f"riesgo {condition['risk_level']}"
        if condition.get("risk_level_gte"):
            return f"riesgo >= {condition['risk_level_gte']}"
        if condition.get("risk_score_gte") is not None:
            return f"score >= {condition['risk_score_gte']}"

    return str(condition)


def _format_domains(scope: dict[str, Any]) -> str:
    """
    Formatea el ámbito de dominios del draft en texto legible

    Args:
        scope(dict[str, Any]): Scope del borrador

    Returns:
        str: Lista de dominios o 'todos tus dominios'
    """
    if not scope:
        return "-"

    if scope.get("target_type") == "all":
        return "todos tus dominios"

    domains = scope.get("domains") or []
    if domains:
        return ", ".join(str(domain) for domain in domains)

    domain_ids = scope.get("domain_ids") or []
    if domain_ids:
        return ", ".join(str(domain_id) for domain_id in domain_ids)

    return "-"


def _format_schedule(schedule: dict[str, Any]) -> str:
    """
    Formatea la frecuencia de ejecución en texto legible

    Args:
        schedule(dict[str, Any]): Schedule del borrador

    Returns:
        str: Descripción de la frecuencia
    """
    if not schedule:
        return "-"

    frequency = schedule.get("frequency")
    at_time = schedule.get("at_time")

    if frequency == "daily":
        return f"diaria a las {at_time}" if at_time else "diaria"
    if frequency == "weekly":
        return f"semanal a las {at_time}" if at_time else "semanal"
    if frequency == "hourly":
        return "cada hora"

    return str(frequency or "-")


def _format_channels(channels: list[dict[str, Any]]) -> str:
    """
    Formatea los canales de notificación en texto legible

    Args:
        channels(list[dict[str, Any]]): Lista de canales del borrador

    Returns:
        str: Descripción de los canales
    """
    if not channels:
        return "-"

    items: list[str] = []
    for channel in channels:
        kind = channel.get("kind")
        if kind == "email" and channel.get("to"):
            items.append(f"email a {channel['to']}")
        elif kind == "webhook" and channel.get("to"):
            items.append(f"webhook a {channel['to']}")
        elif kind:
            items.append(str(kind))

    return ", ".join(items) if items else "-"


def _build_confirmation_summary(draft: dict[str, Any]) -> str:
    """
    Crea el resumen de confirmación con todos los datos del draft para que el usuario los revise

    Args:
        draft(dict[str, Any]): Estado actual del borrador

    Returns:
        str: Mensaje de confirmación formateado
    """

    rule_name = draft.get("rule_name")
    rule_type = draft.get("rule_type")
    condition = draft.get("condition") or {}
    scope = draft.get("scope") or {}
    schedule = draft.get("schedule") or {}
    channels = draft.get("channels") or []

    return with_cancel_hint(
        "Antes de crear la alerta, confirma que esta todo correcto:\n\n"
        f"- Nombre: '{rule_name}'\n"
        f"- Tipo: {_format_rule_type(rule_type)}\n"
        f"- Condicion: {_format_condition(condition, rule_type)}\n"
        f"- Dominios: {_format_domains(scope)}\n"
        f"- Frecuencia: {_format_schedule(schedule)}\n"
        f"- Canales: {_format_channels(channels)}\n\n"
        "Responde **si** para crearla, **no** para cancelar, o escribe el dato que quieres cambiar."
    )


def _missing_domain_response(missing_domains: list[str]) -> dict[str, Any]:
    """
    Crea la respuesta cuando hay dominios del scope que no existen en el inventario

    Args:
        missing_domains (list[str]): Nombres de dominios no encontrados

    Returns:
        dict: Respuesta con mensaje pidiendo corrección
    """
    return {
        "final_user_message": with_cancel_hint(
            f"No encuentro estos dominios en tu inventario: {missing_domains}. "
            "Escribe el dominio correcto para sustituirlo."
        ),
        "cu": "CU-03",
    }


def _offer_domain_registration(domain_name: str) -> dict[str, Any]:
    """
    Ofrece al usuario registrar un dominio que no existe en su inventario

    Args:
        domain_name(str): Nombre del dominio no encontrado

    Returns:
        dict[str, Any]: Respuesta con la oferta de registro
    """
    return {
        "final_user_message": with_cancel_hint(
            f"El dominio **{domain_name}** no está en tu inventario. "
            "¿Quieres registrarlo ahora? Responde **si** para registrarlo "
            "o **no** para indicar otro dominio."
        ),
        "cu": "CU-03",
    }


def _apply_patch_from_message(
    user_id: str,
    session_id: str,
    message: str,
    draft: dict[str, Any],
    *,
    allow_fallback_name: bool,
) -> dict[str, Any]:
    """
    Extrae campos del mensaje del usuario y los aplica al draft en sesión

    Args:
        user_id (str): Identificador del usuario
        session_id (str): Identificador de la sesión
        message (str): Mensaje del usuario
        draft (dict): Estado actual del borrador
        allow_fallback_name (bool): Si True, intenta extraer el nombre de regla como fallback

    Returns:
        dict: Draft actualizado con los nuevos datos extraídos
    """
    patch = regex_extract(message)
    if allow_fallback_name:
        fallback_name = _fallback_rule_name(message, draft)
        if fallback_name and "rule_name" not in patch:
            patch["rule_name"] = fallback_name

    if patch:
        upsert_rule_draft(user_id=user_id, session_id=session_id, patch=patch)
        return get_rule_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}

    return draft


def _format_alert_list(result: dict[str, Any]) -> str:
    """
    Formatea la lista de alertas para mostrarla en el chat

    Args:
        result(dict): Resultado de list_alert_rules_tool con items y count

    Returns:
        str: Texto formateado con la lista de alertas
    """
    items = result.get("items", [])
    count = result.get("count", 0)

    if count == 0:
        return "No tienes alertas configuradas. Puedes crear una eligiendo la opcion **03.- Gestión de alertas**."

    lines = [f"Tienes **{count}** alerta(s) configurada(s):\n"]
    freq_map = {"daily": "diaria", "weekly": "semanal", "hourly": "cada hora"}
    for r in items:
        enabled_icon = "🟢" if r.get("is_enabled") else "🔴"
        rule_type_txt = "caducidad" if r.get("rule_type") == "expiry" else r.get("rule_type", "-")
        freq = (r.get("schedule") or {}).get("frequency", "-")
        freq_txt = freq_map.get(freq, freq)
        domains = r.get("domains") or []
        domains_txt = ", ".join(domains) if domains else "todos los dominios"
        lines.append(
            f"{enabled_icon} **{r['rule_name']}** — Tipo: {rule_type_txt} | "
            f"Frecuencia: {freq_txt} | Dominios: {domains_txt}\n"
        )
    return "\n".join(lines)


def _handle_alert_list(user_id: str, session_id: str) -> dict[str, Any]:
    """
    Gestiona la intencion de listar alertas

    Args:
        user_id(str): ID del usuario
        session_id(str): ID de sesion

    Returns:
        dict[str, Any]: Respuesta con la lista de alertas
    """
    with SessionLocal() as db:
        result = list_alert_rules_tool(user_id=user_id, db=db)

    upsert_rule_draft(
        user_id=user_id,
        session_id=session_id,
        patch={"_active_cu": "CU-03"},
    )

    followup = (
        "\n\n¿Qué quieres hacer? Puedes **crear** una nueva alerta, "
        "**pausar** o **activar** una alerta, o **eliminar** una alerta."
    )

    return {
        "final_user_message": _format_alert_list(result) + followup,
        "cu": "CU-03",
        "show_menu": False,
    }


def _handle_alert_delete(
    user_id: str,
    session_id: str,
    message: str,
    rule_name: str | None,
) -> dict[str, Any]:
    """
    Gestiona el flujo de eliminacion de una alerta con confirmacion.

    Args:
        user_id(str): ID del usuario
        session_id(str): ID de sesion
        message(str): Mensaje actual del usuario
        rule_name(str | None): Nombre de alerta extraido del mensaje inicial

    Returns:
        dict[str, Any]: Respuesta del flujo de eliminacion
    """
    draft_entry = get_rule_draft(user_id=user_id, session_id=session_id)
    draft = draft_entry.get("draft", {}) or {}

    # Estado: esperando que el usuario escriba el nombre de la alerta
    if draft.get("_action") == "delete" and draft.get("_awaiting_rule_name"):
        candidate = message.strip().strip("'\"")
        if len(candidate) < 3:
            return {
                "final_user_message": with_cancel_hint(
                    "Nombre no valido. Escribe el nombre exacto de la alerta."
                ),
                "cu": "CU-03",
            }
        upsert_rule_draft(
            user_id=user_id,
            session_id=session_id,
            patch={"rule_name": candidate, "_awaiting_rule_name": False, "_awaiting_confirmation": True},
        )
        return {
            "final_user_message": with_cancel_hint(
                f"¿Confirmas que quieres eliminar la alerta **{candidate}**? "
                "Esta accion no se puede deshacer.\n\nResponde **si** para confirmar o **no** para cancelar."
            ),
            "cu": "CU-03",
        }

    # Estado: esperando confirmacion
    if draft.get("_action") == "delete" and draft.get("_awaiting_confirmation"):
        if _is_yes(message):
            target = draft.get("rule_name") or rule_name
            with SessionLocal() as db:
                result = delete_alert_rule_tool(user_id=user_id, rule_name=target, db=db)
            clear_rule_draft(user_id=user_id, session_id=session_id)

            if not result.get("deleted"):
                return {
                    "final_user_message": build_menu_message(
                        f"No se pudo eliminar la alerta: {result.get('error', 'error desconocido')}"
                    ),
                    "cu": "CU-03",
                    "show_menu": True,
                }
            return {
                "final_user_message": build_menu_message(
                    f"Alerta **{target}** eliminada correctamente."
                ),
                "cu": "CU-03",
                "show_menu": True,
            }

        if _is_no(message):
            clear_rule_draft(user_id=user_id, session_id=session_id)
            return _cancel_response()

        return {
            "final_user_message": with_cancel_hint(
                "Responde **si** para confirmar la eliminacion o **no** para cancelar."
            ),
            "cu": "CU-03",
        }

    # Primera vez sin nombre detectado: guardar draft y pedir nombre
    if not rule_name:
        upsert_rule_draft(
            user_id=user_id,
            session_id=session_id,
            patch={"_action": "delete", "_awaiting_rule_name": True, "_awaiting_confirmation": False},
        )
        return {
            "final_user_message": with_cancel_hint(
                "¿Que alerta quieres eliminar? Indica el nombre exacto (o entre comillas)."
            ),
            "cu": "CU-03",
        }

    # Primera vez con nombre detectado: guardar draft y pedir confirmacion
    upsert_rule_draft(
        user_id=user_id,
        session_id=session_id,
        patch={"_action": "delete", "rule_name": rule_name, "_awaiting_confirmation": True},
    )
    return {
        "final_user_message": with_cancel_hint(
            f"¿Confirmas que quieres eliminar la alerta **{rule_name}**? "
            "Esta accion no se puede deshacer.\n\nResponde **si** para confirmar o **no** para cancelar."
        ),
        "cu": "CU-03",
    }


def _handle_alert_toggle(
    user_id: str,
    session_id: str,
    message: str,
    rule_name: str | None,
    enabled: bool,
) -> dict[str, Any]:
    """
    Gestiona el flujo de activacion o pausa de una alerta

    Args:
        user_id(str): ID del usuario
        session_id(str): ID de sesion
        message(str): Mensaje actual del usuario
        rule_name(str | None): Nombre de alerta extraido del mensaje inicial
        enabled(bool): True para activar, False para pausar

    Returns:
        dict[str, Any]: Respuesta del flujo de activacion/pausa
    """
    draft_entry = get_rule_draft(user_id=user_id, session_id=session_id)
    draft = draft_entry.get("draft", {}) or {}

    action_txt = "activar" if enabled else "pausar"

    # Estado: esperando que el usuario escriba el nombre de la alerta
    if draft.get("_action") == "toggle" and draft.get("_awaiting_rule_name"):
        candidate = message.strip().strip("'\"")
        d_enabled = draft.get("new_enabled", enabled)
        action_txt_d = "activar" if d_enabled else "pausar"
        if len(candidate) < 3:
            return {
                "final_user_message": with_cancel_hint(
                    "Nombre no valido. Escribe el nombre exacto de la alerta."
                ),
                "cu": "CU-03",
            }
        upsert_rule_draft(
            user_id=user_id,
            session_id=session_id,
            patch={"rule_name": candidate, "_awaiting_rule_name": False, "_awaiting_confirmation": True},
        )
        return {
            "final_user_message": with_cancel_hint(
                f"¿Confirmas que quieres {action_txt_d} la alerta **{candidate}**?\n\n"
                "Responde **si** para confirmar o **no** para cancelar."
            ),
            "cu": "CU-03",
        }

    # Estado: esperando confirmacion
    if draft.get("_action") == "toggle" and draft.get("_awaiting_confirmation"):
        if _is_yes(message):
            target = draft.get("rule_name") or rule_name
            d_enabled = draft.get("new_enabled", enabled)
            action_done = "activada" if d_enabled else "pausada"
            with SessionLocal() as db:
                result = toggle_alert_rule_tool(user_id=user_id, rule_name=target, enabled=d_enabled, db=db)
            clear_rule_draft(user_id=user_id, session_id=session_id)

            if not result.get("updated"):
                return {
                    "final_user_message": build_menu_message(
                        f"No se pudo {action_txt} la alerta: {result.get('error', 'error desconocido')}"
                    ),
                    "cu": "CU-03",
                    "show_menu": True,
                }
            return {
                "final_user_message": build_menu_message(
                    f"Alerta **{target}** {action_done} correctamente."
                ),
                "cu": "CU-03",
                "show_menu": True,
            }

        if _is_no(message):
            clear_rule_draft(user_id=user_id, session_id=session_id)
            return _cancel_response()

        return {
            "final_user_message": with_cancel_hint(
                "Responde **si** para confirmar o **no** para cancelar."
            ),
            "cu": "CU-03",
        }

    # Primera vez sin nombre detectado: guardar draft y pedir nombre
    if not rule_name:
        upsert_rule_draft(
            user_id=user_id,
            session_id=session_id,
            patch={"_action": "toggle", "new_enabled": enabled,
                   "_awaiting_rule_name": True, "_awaiting_confirmation": False},
        )
        return {
            "final_user_message": with_cancel_hint(
                f"¿Que alerta quieres {action_txt}? Indica el nombre exacto (o entre comillas)."
            ),
            "cu": "CU-03",
        }

    # Primera vez con nombre detectado: guardar draft y pedir confirmacion
    upsert_rule_draft(
        user_id=user_id,
        session_id=session_id,
        patch={"_action": "toggle", "rule_name": rule_name, "new_enabled": enabled, "_awaiting_confirmation": True},
    )
    return {
        "final_user_message": with_cancel_hint(
            f"¿Confirmas que quieres {action_txt} la alerta **{rule_name}**?\n\n"
            "Responde **si** para confirmar o **no** para cancelar."
        ),
        "cu": "CU-03",
    }


def handle_cu03(
    user_id: str,
    session_id: str,
    message: str,
    model: str,
    client: OpenAI,
) -> dict[str, Any]:
    """
    Gestiona logica conversacional para obtener los datos necesarios para generar una regla de
    alerta. Mantiene el estado entre los mensajes con un draft en sesión hasta obtener todos
    datos necesarios para generar la alerta o cancelar si el usuario quiere.
    En este caso no se usan los parámetros model ni client pero hay que pasarlos para mantener consistencia

    Args:
        user_id(str): Identificador del usuario
        session_id(str): Identificador de la sesión de chat activa
        message(str): Último mensaje enviado por el usuario
        model(str): Identificador del modelo LLM a usar si se necesita
        client (OpenAI): Cliente OpenAI inicializado

    Returns:
        dict[str, Any]: Respuesta con la clave `final_user_message` y flags de control (`show_menu`, `option`)
    """
    draft_entry = get_rule_draft(user_id=user_id, session_id=session_id)
    draft = draft_entry.get("draft", {}) or {}

    if not draft:
        log_event(
            logger,
            level=20,
            event="cu03_flow_started",
            message=f"CU-03 iniciado por usuario {user_id}",
            session_id=session_id,
            user_id=user_id,
        )

    if not draft or not draft.get("_action"):
        crud = extract_cu03_crud_intent(message)
        intent = crud.get("intent")

        if intent == "list":
            return _handle_alert_list(user_id=user_id, session_id=session_id)

        if intent == "delete":
            return _handle_alert_delete(
                user_id=user_id,
                session_id=session_id,
                message=message,
                rule_name=crud.get("rule_name"),
            )

        if intent == "pause":
            return _handle_alert_toggle(
                user_id=user_id,
                session_id=session_id,
                message=message,
                rule_name=crud.get("rule_name"),
                enabled=False,
            )

        if intent == "enable":
            return _handle_alert_toggle(
                user_id=user_id,
                session_id=session_id,
                message=message,
                rule_name=crud.get("rule_name"),
                enabled=True,
            )

        # Sin intencion CRUD ni datos de creacion muestra submenu
        if not draft:
            patch = regex_extract(message)
            has_creation_data = any(k in patch for k in ("rule_type", "condition", "channels", "scope", "schedule"))
            if not has_creation_data:
                upsert_rule_draft(
                    user_id=user_id,
                    session_id=session_id,
                    patch={"_active_cu": "CU-03"},
                )
                return {
                    "final_user_message": with_cancel_hint(
                        "¿Qué quieres hacer con tus alertas?\n\n"
                        "- **Ver** mis alertas\n"
                        "- **Crear** una nueva alerta\n"
                        "- **Pausar** una alerta\n"
                        "- **Activar** una alerta\n"
                        "- **Eliminar** una alerta"
                    ),
                    "cu": "CU-03",
                }

    if draft.get("_action") == "delete":
        return _handle_alert_delete(
            user_id=user_id,
            session_id=session_id,
            message=message,
            rule_name=draft.get("rule_name"),
        )

    if draft.get("_action") == "toggle":
        return _handle_alert_toggle(
            user_id=user_id,
            session_id=session_id,
            message=message,
            rule_name=draft.get("rule_name"),
            enabled=draft.get("new_enabled", True),
        )

    if _wants_exit(message):
        clear_rule_draft(user_id=user_id, session_id=session_id)
        log_event(
            logger,
            level=20,
            event="cu03_flow_cancelled",
            message=f"CU-03 cancelado por usuario {user_id}",
            session_id=session_id,
            user_id=user_id,
        )
        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id,
            session_id=session_id,
            event="alert_rule_cancelled",
            payload={"reason": "exit_command", "rule_name": draft.get("rule_name")},
        )
        return _cancel_response()

    # --- Estado: esperando confirmación para registrar dominio ---
    if draft.get("_awaiting_domain_register_confirm"):
        domain_to_register = draft.get("_domain_to_register", "")

        if _is_yes(message):
            with SessionLocal() as db:
                register_domain_cu02(
                    user_id=user_id,
                    domain_name=domain_to_register,
                    tags=[],
                    status="activo",
                    db=db,
                )

            upsert_rule_draft(
                user_id=user_id,
                session_id=session_id,
                patch={
                    "_awaiting_domain_register_confirm": False,
                    "_domain_to_register": None,
                },
            )
            draft = get_rule_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}

            # Reintentar resolve_scope con el dominio ya registrado
            with SessionLocal() as db:
                rs = resolve_scope(user_id=user_id, scope=draft.get("scope", {}), db=db)

            if rs.get("missing_domains"):
                upsert_rule_draft(
                    user_id=user_id,
                    session_id=session_id,
                    patch={
                        "_awaiting_scope_correction": True,
                        "_awaiting_confirmation": False,
                        "_confirmed": False,
                        "_missing_domains": rs["missing_domains"],
                    },
                )
                return _missing_domain_response(rs["missing_domains"])

            upsert_rule_draft(
                user_id=user_id,
                session_id=session_id,
                patch={"_awaiting_confirmation": True, "_confirmed": False},
            )
            draft = get_rule_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}
            return {"final_user_message": _build_confirmation_summary(draft), "cu": "CU-03"}

        if _is_no(message):
            upsert_rule_draft(
                user_id=user_id,
                session_id=session_id,
                patch={
                    "_awaiting_domain_register_confirm": False,
                    "_domain_to_register": None,
                    "_awaiting_scope_correction": True,
                    "_missing_domains": [domain_to_register],
                },
            )
            return _missing_domain_response([domain_to_register])

        return _offer_domain_registration(domain_to_register)

    # --- Estado: esperando corrección de dominios no encontrados en inventario ---
    if draft.get("_awaiting_scope_correction"):
        updated_draft = _apply_patch_from_message(
            user_id=user_id,
            session_id=session_id,
            message=message,
            draft=draft,
            allow_fallback_name=False,
        )
        if updated_draft != draft and (updated_draft.get("scope") or {}).get("domains"):
            upsert_rule_draft(
                user_id=user_id,
                session_id=session_id,
                patch={
                    "_awaiting_scope_correction": False,
                    "_awaiting_confirmation": True,
                    "_confirmed": False,
                    "_last_question_field": "scope",
                },
            )
            draft = get_rule_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}
            return {"final_user_message": _build_confirmation_summary(draft), "cu": "CU-03"}

        return _missing_domain_response(draft.get("_missing_domains") or [])

    # --- Estado: esperando confirmación final ---
    if draft.get("_awaiting_confirmation"):
        if _is_yes(message):
            upsert_rule_draft(
                user_id=user_id,
                session_id=session_id,
                patch={"_confirmed": True, "_awaiting_confirmation": False},
            )
            draft = get_rule_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}
        elif _is_no(message):
            clear_rule_draft(user_id=user_id, session_id=session_id)
            log_event(
                logger,
                level=20,
                event="cu03_flow_cancelled",
                message=f"CU-03 cancelado en confirmación por usuario {user_id}",
                session_id=session_id,
                user_id=user_id,
            )
            write_audit_event(
                trace_id=trace_id_ctx.get(),
                user_id=user_id,
                session_id=session_id,
                event="alert_rule_cancelled",
                payload={"reason": "user_rejected_confirmation", "rule_name": draft.get("rule_name")},
            )
            return _cancel_response()
        else:
            updated_draft = _apply_patch_from_message(
                user_id=user_id,
                session_id=session_id,
                message=message,
                draft=draft,
                allow_fallback_name=False,
            )
            if updated_draft != draft:
                upsert_rule_draft(
                    user_id=user_id,
                    session_id=session_id,
                    patch={"_awaiting_confirmation": True, "_confirmed": False},
                )
                draft = get_rule_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}
                return {"final_user_message": _build_confirmation_summary(draft), "cu": "CU-03"}

            return {
                "final_user_message": with_cancel_hint(
                    "¿Confirmas la creacion? Responde **si** para crear, **no** para cancelar, o escribe el dato que quieres cambiar."  # noqa: E501
                ),
                "cu": "CU-03",
            }

    draft = _apply_patch_from_message(
        user_id=user_id,
        session_id=session_id,
        message=message,
        draft=draft,
        allow_fallback_name=True,
    )

    missing = _missing(draft)
    if missing:
        asked = missing[:2]
        question = build_question_for_missing(draft=draft, missing=missing)
        upsert_rule_draft(
            user_id=user_id,
            session_id=session_id,
            patch={
                "_active_cu": "CU-03",
                "_pending_fields": asked,
                "_last_question_field": asked[0],
                "_awaiting_confirmation": False,
                "_confirmed": False,
            },
        )
        return {"final_user_message": question, "cu": "CU-03"}

    validated = validate_alert_rule_dsl(user_id=user_id, rule_dsl=draft)
    if not validated.get("valid"):
        issues = validated.get("issues") or []
        return {
            "final_user_message": with_cancel_hint(
                f"No puedo crear la alerta aun. Problemas: {issues}"
            ),
            "cu": "CU-03",
        }

    if not draft.get("_confirmed"):
        upsert_rule_draft(
            user_id=user_id,
            session_id=session_id,
            patch={
                "_active_cu": "CU-03",
                "_awaiting_confirmation": True,
                "_confirmed": False,
            },
        )
        draft = get_rule_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}
        return {"final_user_message": _build_confirmation_summary(draft), "cu": "CU-03"}

    try:
        with SessionLocal() as db:
            normalized = validated["normalized_rule"]

            rs = resolve_scope(user_id=user_id, scope=draft["scope"], db=db)
            if rs.get("missing_domains"):
                missing = rs["missing_domains"]
                if len(missing) == 1:
                    # Un solo dominio missing: ofrecer registrarlo
                    upsert_rule_draft(
                        user_id=user_id,
                        session_id=session_id,
                        patch={
                            "_awaiting_domain_register_confirm": True,
                            "_domain_to_register": missing[0],
                            "_awaiting_confirmation": False,
                            "_confirmed": False,
                        },
                    )
                    return _offer_domain_registration(missing[0])
                else:
                    # Varios dominios missing: pedir corrección
                    upsert_rule_draft(
                        user_id=user_id,
                        session_id=session_id,
                        patch={
                            "_awaiting_scope_correction": True,
                            "_awaiting_confirmation": False,
                            "_confirmed": False,
                            "_last_question_field": "scope",
                            "_missing_domains": missing,
                        },
                    )
                    return _missing_domain_response(missing)

            normalized["scope"]["domain_ids"] = rs.get("domain_ids", [])
            up = upsert_alert_rule(user_id=user_id, mode="create", rule_dsl=normalized, db=db)
            rule_id = up["rule_id"]

            set_rule_targets(
                user_id=user_id,
                rule_id=rule_id,
                session_id=session_id,
                resolved_scope=rs,
                db=db,
            )
            register_rule_schedule(
                user_id=user_id,
                rule_id=rule_id,
                session_id=session_id,
                schedule=normalized["schedule"],
                db=db,
            )
            db.commit()
    except Exception as e:
        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id,
            session_id=session_id,
            event="alert_rule_failed",
            payload={
                "rule_name": draft.get("rule_name"),
                "error": str(e),
            },
        )
        raise

    write_audit_event(
        trace_id=trace_id_ctx.get(),
        user_id=user_id,
        session_id=session_id,
        event="alert_rule_created",
        payload={
            "rule_id": rule_id,
            "rule_name": draft.get("rule_name"),
            "domain_names": (draft.get("scope") or {}).get("domains", []),
            "severity": draft.get("severity"),
        },
    )

    clear_rule_draft(user_id=user_id, session_id=session_id)

    return {
        "final_user_message": f"Alerta creada (rule_id={rule_id}). Te avisare segun la configuracion.",
        "cu": "CU-03",
        "rule_id": rule_id,
        "show_menu": True,
    }
