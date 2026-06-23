from __future__ import annotations

import re
from typing import Any

from openai import OpenAI

from app.db.session import SessionLocal
from app.orchestrator.cu02.extractors import regex_extract, extract_crud_intent, _DOMAIN_RE
from app.orchestrator.cu02.questions import (
    build_question_for_missing,
    build_tags_question,
    with_cancel_hint,
)
from app.orchestrator.router import build_menu_message
from app.storage.domain_draft_store import (
    clear_domain_draft,
    get_domain_draft,
    upsert_domain_draft,
)
from app.tools.cu02 import register_domain, delete_domain_tool, update_domain_tool, list_user_domains
from app.storage.audit_store import write_audit_event
from app.core.logging import get_logger, log_event, trace_id_ctx, session_id_ctx

logger = get_logger("cu02.handler")


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
    confirm_commands = {
        "si",
        "sí",
        "s",
        "ok",
        "vale",
        "confirmar",
        "confirmo",
        "registrar",
        "registrar",
        "adelante",
        "de acuerdo"
    }
    return text in confirm_commands or (("confirm" in text or "crea" in text))


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
            "Gestión de dominios cancelado. Puedes elegir otra opción."
        ),
        "cu": "CU-02",
        "show_menu": True,
    }


def _build_confirmation_summary(draft: dict[str, Any]) -> str:
    """
    Crea el resumen de confirmación con todos los datos del draft para que el usuario los revise

    Args:
        draft(dict[str, Any]): Estado actual del borrador

    Returns:
        str: Mensaje de confirmación formateado
    """

    domain = draft.get("domain_name", "-")
    tags = draft.get("tags")
    tags_txt = ", ".join(tags) if tags else "ninguna"

    return with_cancel_hint(
        f"Confirma el registro del dominio:\n\n"
        f"- Dominio: **{domain}**\n"
        f"- Etiquetas: {tags_txt}\n\n"
        "Responde **si** para registrar, **no** para cancelar."
    )


def _format_domain_list(result: dict) -> str:
    """
    Formatea la lista de dominios para mostrarla en el chat

    Args:
        result(dict): Resultado de list_user_domains con items y count

    Returns:
        str: Texto formateado con tabla de dominios
    """
    items = result.get("items", [])
    count = result.get("count", 0)

    if count == 0:
        return "No tienes dominios registrados. Puedes registrar uno eligiendo la opción **02.- Gestión de dominios**."

    lines = [f"Tienes **{count}** dominio(s) registrado(s):\n"]
    for item in items:
        score = item.get("reputation_score", 0.0)
        status_icon = "🟢" if item.get("status") == "activo" else "🔴"
        tags_txt = ", ".join(item.get("tags") or []) or "sin etiquetas"
        expiry = item.get("expiration_date")
        expiry_txt = expiry.strftime("%d/%m/%Y") if expiry else "desconocida"
        lines.append(
            f"{status_icon} **{item['domain_name']}** — Score: {score:.0f}/100 | "
            f"Tags: {tags_txt} | Expira: {expiry_txt} \n"
        )
    return "\n".join(lines)


def _handle_list(user_id: str, session_id: str) -> dict[str, Any]:
    """
    Gestiona la intención de listar dominios y se mantiene en CU02

    Args:
        user_id(str): ID del usuario
        session_id(str): ID de sesión

    Returns:
        dict[str, Any]: Respuesta con la lista de dominios y seguimiento en CU-02
    """
    with SessionLocal() as db:
        result = list_user_domains(user_id=user_id, db=db)

    upsert_domain_draft(
        user_id=user_id,
        session_id=session_id,
        patch={"_active_cu": "CU-02"},
    )

    followup = "\n\n¿Qué quieres hacer? Puedes **eliminar** un dominio, **actualizar** sus tags o estado, o **registrar** uno nuevo."  # noqa: E501

    return {
        "final_user_message": _format_domain_list(result) + followup,
        "cu": "CU-02",
        "show_menu": False,
    }


def _handle_delete(
    user_id: str,
    session_id: str,
    message: str,
    domain_name: str | None,
) -> dict[str, Any]:
    """
    Gestiona el flujo de eliminación de un dominio con confirmación

    Args:
        user_id(str): ID del usuario
        session_id(str): ID de sesión
        message(str): Mensaje del usuario
        domain_name(str | None): Nombre del dominio

    Returns:
        dict[str, Any]: Respuesta del flujo de eliminación
    """
    draft_entry = get_domain_draft(user_id=user_id, session_id=session_id)
    draft = draft_entry.get("draft", {}) or {}

    if _wants_exit(message):
        clear_domain_draft(user_id=user_id, session_id=session_id)
        return _cancel_response()

    # Espera la confirmación del usuario
    if draft.get("_action") == "delete" and draft.get("_awaiting_confirmation"):
        if _is_yes(message):
            target = draft.get("domain_name")
            with SessionLocal() as db:
                result = delete_domain_tool(user_id=user_id, domain_name=target, db=db)
            clear_domain_draft(user_id=user_id, session_id=session_id)

            if not result.get("deleted"):
                return {
                    "final_user_message": build_menu_message(
                        f"No se pudo eliminar el dominio: {result.get('error', 'error desconocido')}"
                    ),
                    "cu": "CU-02",
                    "show_menu": True,
                }
            return {
                "final_user_message": build_menu_message(
                    f"Dominio **{target}** eliminado correctamente."
                ),
                "cu": "CU-02",
                "show_menu": True,
            }

        if _is_no(message):
            clear_domain_draft(user_id=user_id, session_id=session_id)
            return _cancel_response()

        return {
            "final_user_message": with_cancel_hint(
                "Responde **sí** para confirmar la eliminación o **no** para cancelar."
            ),
            "cu": "CU-02",
        }

    # Continuar flujo activo: extraer dominio del mensaje si no viene en el draft
    if draft.get("_action") == "delete" and not draft.get("_awaiting_confirmation") and not domain_name:
        from app.orchestrator.cu02.extractors import _DOMAIN_RE
        found = _DOMAIN_RE.findall(message)
        if found:
            domain_name = found[0].lower()

    # Si no hay dominio, guardar draft para mantener la sesión y pedir el nombre
    if not domain_name:
        upsert_domain_draft(
            user_id=user_id,
            session_id=session_id,
            patch={"_action": "delete", "_active_cu": "CU-02"},
        )
        return {
            "final_user_message": with_cancel_hint(
                "¿Qué dominio quieres eliminar? Indícame el nombre exacto."
            ),
            "cu": "CU-02",
        }

    upsert_domain_draft(
        user_id=user_id,
        session_id=session_id,
        patch={"_action": "delete", "domain_name": domain_name, "_awaiting_confirmation": True},
    )
    return {
        "final_user_message": with_cancel_hint(
            f"¿Confirmas que quieres eliminar **{domain_name}**? "
            "Esta acción no se puede deshacer.\n\nResponde **sí** para confirmar o **no** para cancelar."
        ),
        "cu": "CU-02",
    }


def _handle_update(
    user_id: str,
    session_id: str,
    message: str,
    domain_name: str | None,
    new_status: str | None,
    new_tags: list[str] | None,
) -> dict[str, Any]:
    """
    Gestiona el flujo de actualización de las tags o del estado de un dominio

    Args:
        user_id(str): ID del usuario
        session_id(str): ID de sesión
        message(str): Mensaje del usuario
        domain_name(str | None): Dominio a actualizar
        new_status(str | None): Nuevo estado detectado
        new_tags(list[str] | None): Nuevas tags detectadas

    Returns:
        dict[str, Any]: Respuesta del flujo de actualización
    """
    draft_entry = get_domain_draft(user_id=user_id, session_id=session_id)
    draft = draft_entry.get("draft", {}) or {}

    if _wants_exit(message):
        clear_domain_draft(user_id=user_id, session_id=session_id)
        return _cancel_response()

    # Esperando tags cuando la intención es actualizar las tags pero no se dieron en el mensaje
    if draft.get("_action") == "update" and draft.get("_awaiting_tags"):
        raw = [t.strip().lower() for t in re.split(r"[,;\s]+", message.strip()) if t.strip() and len(t.strip()) <= 20]
        tags_parsed = raw[:10] if raw else []
        upsert_domain_draft(
            user_id=user_id,
            session_id=session_id,
            patch={"new_tags": tags_parsed, "_awaiting_tags": False, "_awaiting_confirmation": True},
        )
        draft = get_domain_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}
        target = draft.get("domain_name")
        return {
            "final_user_message": with_cancel_hint(
                f"¿Confirmas cambiar las etiquetas de **{target}** a: {', '.join(tags_parsed) or 'ninguna'}?\n\n"
                "Responde **sí** para confirmar o **no** para cancelar."
            ),
            "cu": "CU-02",
        }

    if draft.get("_action") == "update" and draft.get("_awaiting_confirmation"):
        if _is_yes(message):
            target = draft.get("domain_name")
            d_tags = draft.get("new_tags")
            d_status = draft.get("new_status")
            with SessionLocal() as db:
                result = update_domain_tool(
                    user_id=user_id,
                    domain_name=target,
                    tags=d_tags,
                    status=d_status,
                    db=db,
                )
            clear_domain_draft(user_id=user_id, session_id=session_id)

            if not result.get("updated"):
                return {
                    "final_user_message": build_menu_message(
                        f"No se pudo actualizar el dominio: {result.get('error', 'error desconocido')}"
                    ),
                    "cu": "CU-02",
                    "show_menu": True,
                }
            return {
                "final_user_message": build_menu_message(
                    f"Dominio **{target}** actualizado correctamente."
                ),
                "cu": "CU-02",
                "show_menu": True,
            }

        if _is_no(message):
            clear_domain_draft(user_id=user_id, session_id=session_id)
            return _cancel_response()

        return {
            "final_user_message": with_cancel_hint("Responde **sí** para confirmar o **no** para cancelar."),
            "cu": "CU-02",
        }

    if draft.get("_action") == "update" and not domain_name:
        found = _DOMAIN_RE.findall(message)
        if found:
            domain_name = found[0].lower()
        if new_status is None:
            re_crud = extract_crud_intent(message)
            if re_crud.get("intent") == "update_status":
                new_status = re_crud.get("new_status")

    # Si no hay dominio, guardar draft para mantener sesión y pedir el nombre
    if not domain_name:
        upsert_domain_draft(
            user_id=user_id,
            session_id=session_id,
            patch={"_action": "update", "_active_cu": "CU-02"},
        )
        return {
            "final_user_message": with_cancel_hint(
                "¿Qué dominio quieres modificar?\n\n"
                "Puedes cambiar:\n"
                "- **Tags**: indica el dominio y luego las etiquetas (ej: *gato.com tags: marca, cliente*)\n"
                "- **Estado**: escribe *activa* o *desactiva* seguido del dominio (ej: *desactiva gato.com*)"
            ),
            "cu": "CU-02",
        }

    if new_status:
        status_txt = "inactivo" if new_status == "inactivo" else "activo"
        upsert_domain_draft(
            user_id=user_id,
            session_id=session_id,
            patch={"_action": "update", "domain_name": domain_name,
                   "new_status": new_status, "_awaiting_confirmation": True},
        )
        return {
            "final_user_message": with_cancel_hint(
                f"¿Confirmas cambiar el estado de **{domain_name}** a **{status_txt}**?\n\n"
                "Responde **sí** para confirmar o **no** para cancelar."
            ),
            "cu": "CU-02",
        }

    # Pide las nuevas tags
    upsert_domain_draft(
        user_id=user_id,
        session_id=session_id,
        patch={"_action": "update", "domain_name": domain_name,
               "_awaiting_tags": True, "_awaiting_confirmation": False},
    )
    return {
        "final_user_message": with_cancel_hint(
            f"¿Cuáles serán las nuevas etiquetas de **{domain_name}**? "
            "Escríbelas separadas por comas (o escribe **ninguna** para dejarlas vacías)."
        ),
        "cu": "CU-02",
    }


def handle_cu02(
    user_id: str,
    session_id: str,
    message: str,
    model: str,
    client: OpenAI,
) -> dict[str, Any]:
    """
    Gestiona la conversación para registrar un dominio (CU-02)
    Recoge domain_name (obligatorio) y tags (opcional), muestra confirmación
    y persiste el dominio con su enriquecimiento

    Args:
        user_id(str): Identificador del usuario
        session_id(str): Identificador de la sesión
        message(str): Último mensaje del usuario
        model(str): Modelo LLM (no usado, por consistencia de firma)
        client(OpenAI): Cliente OpenAI (no usado, por consistencia de firma)

    Returns:
        dict[str, Any]: Respuesta con final_user_message y flags de control
    """
    draft_entry = get_domain_draft(user_id=user_id, session_id=session_id)
    draft = draft_entry.get("draft", {}) or {}

    if not draft:
        log_event(
            logger,
            level=20,
            event="cu02_flow_started",
            message=f"CU-02 iniciado por usuario {user_id}",
            session_id=session_id,
            user_id=user_id,
        )

    # CRUD detecta la intención si no hay un draft activo
    if not draft or not draft.get("_action"):
        crud = extract_crud_intent(message)
        intent = crud.get("intent")

        if intent == "list":
            return _handle_list(user_id=user_id, session_id=session_id)

        if intent == "delete":
            return _handle_delete(
                user_id=user_id,
                session_id=session_id,
                message=message,
                domain_name=crud.get("domain_name"),
            )

        if intent in ("update_status", "update_tags"):
            return _handle_update(
                user_id=user_id,
                session_id=session_id,
                message=message,
                domain_name=crud.get("domain_name"),
                new_status=crud.get("new_status"),
                new_tags=crud.get("new_tags"),
            )

        # Primera entrada sin intención CRUD: mostrar submenú si no viene dominio en el mensaje
        if not draft:
            patch = regex_extract(message)
            if not patch.get("domain_name"):
                upsert_domain_draft(
                    user_id=user_id,
                    session_id=session_id,
                    patch={"_active_cu": "CU-02"},
                )
                return {
                    "final_user_message": with_cancel_hint(
                        "¿Qué quieres hacer con tus dominios?\n\n"
                        "- **Registrar** un nuevo dominio\n"
                        "- **Ver** mis dominios\n"
                        "- **Eliminar** un dominio\n"
                        "- **Actualizar** tags o estado de un dominio"
                    ),
                    "cu": "CU-02",
                }

    # Continuar con el borrado o la actualizacion
    if draft.get("_action") == "delete":
        return _handle_delete(
            user_id=user_id,
            session_id=session_id,
            message=message,
            domain_name=draft.get("domain_name"),
        )

    if draft.get("_action") == "update":
        return _handle_update(
            user_id=user_id,
            session_id=session_id,
            message=message,
            domain_name=draft.get("domain_name"),
            new_status=draft.get("new_status"),
            new_tags=draft.get("new_tags"),
        )

    if _wants_exit(message):
        clear_domain_draft(user_id=user_id, session_id=session_id)
        log_event(
            logger,
            level=20,
            event="cu02_flow_cancelled",
            message=f"CU-02 cancelado por usuario {user_id}",
            session_id=session_id,
            user_id=user_id,
        )
        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id,
            session_id=session_id_ctx.get(),
            event="domain_registration_cancelled",
            payload={"reason": "exit_command", "domain_name": draft.get("domain_name")},
        )
        return _cancel_response()

    # --- Estado: esperando confirmación final ---
    if draft.get("_awaiting_confirmation"):
        if _is_yes(message):
            with SessionLocal() as db:
                result = register_domain(
                    user_id=user_id,
                    domain_name=draft["domain_name"],
                    tags=draft.get("tags") or [],
                    status="activo",
                    db=db,
                )
            clear_domain_draft(user_id=user_id, session_id=session_id)

            if not result.get("created"):
                return {
                    "final_user_message": build_menu_message(
                        f"No se pudo registrar el dominio: {result.get('error', 'error desconocido')}"
                    ),
                    "cu": "CU-02",
                    "show_menu": True,
                }

            return {
                "final_user_message": build_menu_message(
                    f"Dominio **{draft['domain_name']}** registrado correctamente. "
                    f"Score de reputación inicial: {result.get('reputation_score', 0.0)}"
                ),
                "cu": "CU-02",
                "domain_id": result.get("domain_id"),
                "show_menu": True,
            }

        if _is_no(message):
            clear_domain_draft(user_id=user_id, session_id=session_id)
            log_event(
                logger,
                level=20,
                event="cu02_flow_cancelled",
                message=f"CU-02 cancelado en confirmación por usuario {user_id}",
                session_id=session_id,
                user_id=user_id,
            )
            write_audit_event(
                trace_id=trace_id_ctx.get(),
                user_id=user_id,
                session_id=session_id_ctx.get(),
                event="domain_registration_cancelled",
                payload={"reason": "user_rejected_confirmation", "domain_name": draft.get("domain_name")},
            )
            return _cancel_response()

        return {
            "final_user_message": with_cancel_hint(
                "Responde **si** para registrar el dominio o **no** para cancelar."
            ),
            "cu": "CU-02",
        }

    # --- Estado: esperando respuesta de tags ---
    if draft.get("_awaiting_tags"):
        patch = regex_extract(message)
        tags = patch.get("tags")

        # Si no extrajo tags con prefijo pero tampoco es "no", intenta parsear texto libre
        if tags is None and not _is_no(message):
            raw = [t.strip().lower() for t in re.split(r"[,;\s]+", message.strip()) if t.strip() and len(t.strip()) <= 20]  # noqa: E501
            tags = raw[:10] if raw else None

        upsert_domain_draft(
            user_id=user_id,
            session_id=session_id,
            patch={
                "tags": tags if tags is not None else [],
                "_awaiting_tags": False,
                "_awaiting_confirmation": True,
            },
        )
        draft = get_domain_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}
        return {"final_user_message": _build_confirmation_summary(draft), "cu": "CU-02"}

    # --- Extracción normal del mensaje ---
    patch = regex_extract(message)
    if patch:
        upsert_domain_draft(user_id=user_id, session_id=session_id, patch=patch)
        draft = get_domain_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}

    # --- Campo obligatorio pendiente ---
    if not draft.get("domain_name"):
        upsert_domain_draft(
            user_id=user_id,
            session_id=session_id,
            patch={"_active_cu": "CU-02", "_awaiting_tags": False, "_awaiting_confirmation": False},
        )
        return {
            "final_user_message": build_question_for_missing(draft, ["domain_name"]),
            "cu": "CU-02",
        }

    # --- domain_name ok, preguntar tags si no se han dado aún ---
    if "tags" not in draft:
        upsert_domain_draft(
            user_id=user_id,
            session_id=session_id,
            patch={"_active_cu": "CU-02", "_awaiting_tags": True, "_awaiting_confirmation": False},
        )
        return {
            "final_user_message": build_tags_question(draft["domain_name"]),
            "cu": "CU-02",
        }

    # --- Todos los datos recogidos → confirmación ---
    upsert_domain_draft(
        user_id=user_id,
        session_id=session_id,
        patch={"_awaiting_confirmation": True},
    )
    draft = get_domain_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}
    return {"final_user_message": _build_confirmation_summary(draft), "cu": "CU-02"}
