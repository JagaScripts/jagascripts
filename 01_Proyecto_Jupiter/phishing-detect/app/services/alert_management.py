from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import get_logger, session_id_ctx, trace_id_ctx, log_event
from app.db.models import AlertRule, AlertRuleTarget, Domain
from app.storage.audit_store import write_audit_event

logger = get_logger("services.alert_management")


def list_alert_rules(user_id: str, *, db: Session) -> dict[str, Any]:
    """
    Lista las alertas del usuario ordenadas por fecha de creación

    Args:
        user_id(str): ID del usuario
        db(Session): Sesión de BD

    Returns:
        dict[str, Any]: Lista de reglas
    """
    rows = db.execute(
        select(AlertRule)
        .where(AlertRule.user_id == user_id)
        .order_by(AlertRule.created_at.desc())
    ).scalars().all()

    rule_ids = [r.id for r in rows]
    domains_by_rule: dict[str, list[str]] = {}
    if rule_ids:
        targets = db.execute(
            select(AlertRuleTarget.rule_id, Domain.domain_name)
            .join(Domain, AlertRuleTarget.domain_id == Domain.id)
            .where(AlertRuleTarget.rule_id.in_(rule_ids))
        ).all()
        for rule_id, domain_name in targets:
            domains_by_rule.setdefault(rule_id, []).append(domain_name)

    items = [
        {
            "rule_id": r.id,
            "rule_name": r.name,
            "rule_type": r.rule_type,
            "is_enabled": r.is_enabled,
            "severity": r.severity,
            "schedule": r.schedule_json or {},
            "condition": (r.logic_json or {}).get("condition", {}),
            "created_at": r.created_at,
            "domains": domains_by_rule.get(r.id, []),
        }
        for r in rows
    ]

    return {"items": items, "count": len(items)}


def delete_alert_rule(rule_id: str, user_id: str, *, db: Session) -> dict[str, Any]:
    """
    Elimina una regla de alerta

    Args:
        rule_id(str): ID de la regla a eliminar
        user_id(str): ID del usuario
        db(Session): Sesión de BD

    Returns:
        dict[str, Any]: Resultado con deleted=True/False
    """
    try:
        rule = db.query(AlertRule).filter(
            AlertRule.id == rule_id,
            AlertRule.user_id == user_id,
        ).first()

        if not rule:
            return {"deleted": False, "error": "Regla no encontrada o no pertenece al usuario."}

        rule_name = rule.name
        db.delete(rule)
        db.commit()

        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id,
            session_id=session_id_ctx.get(),
            event="alert_rule_deleted",
            payload={"rule_id": rule_id, "rule_name": rule_name},
        )

        log_event(
            logger,
            level=20,
            event="alert_rule_delete_complete",
            message="Regla eliminada",
            extra={"rule_id": rule_id, "rule_name": rule_name},
        )
        return {"deleted": True, "rule_name": rule_name}

    except Exception as e:
        db.rollback()
        log_event(
            logger,
            level=40,
            event="alert_rule_delete_error",
            message="Error eliminando regla",
            extra={"rule_id": rule_id, "error": str(e)},
            exc_info=True,
        )
        return {"deleted": False, "error": str(e)}


def toggle_alert_rule(rule_id: str, user_id: str, enabled: bool, *, db: Session) -> dict[str, Any]:
    """
    Activa o pausa una regla de alerta cambiando is_enabled

    Args:
        rule_id(str): ID de la regla
        user_id(str): ID del usuario
        enabled(bool): True para activar, False para pausar
        db(Session): Sesión de BD

    Returns:
        dict[str, Any]: Resultado con updated=True/False
    """
    try:
        rule = db.query(AlertRule).filter(
            AlertRule.id == rule_id,
            AlertRule.user_id == user_id,
        ).first()

        if not rule:
            return {"updated": False, "error": "Regla no encontrada o no pertenece al usuario."}

        rule.is_enabled = enabled
        db.commit()

        action = "activada" if enabled else "pausada"
        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id,
            session_id=session_id_ctx.get(),
            event="alert_rule_toggled",
            payload={"rule_id": rule_id, "rule_name": rule.name, "enabled": enabled, "action": action},
        )

        log_event(
            logger,
            level=20,
            event="alert_rule_toggle_complete",
            message=f"Regla {action}",
            extra={"rule_id": rule_id, "rule_name": rule.name, "enabled": enabled, "action": action},
        )
        return {"updated": True, "rule_id": rule_id, "rule_name": rule.name, "is_enabled": enabled}

    except Exception as e:
        db.rollback()
        log_event(
            logger,
            level=40,
            event="alert_rule_toggle_error",
            message="Error actualizando regla",
            extra={"rule_id": rule_id, "error": str(e)},
            exc_info=True,
        )
        return {"updated": False, "error": str(e)}
