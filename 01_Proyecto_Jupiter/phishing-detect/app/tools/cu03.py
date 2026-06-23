from __future__ import annotations
import uuid
from typing import Any
from pydantic import ValidationError
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.models.dsl import AlertRuleDSL
from app.db.models import Domain, AlertRule, AlertRuleTarget, ScheduleJob
from app.storage.rule_draft_store import get_rule_draft
from app.services.alert_management import (
    list_alert_rules,
    delete_alert_rule,
    toggle_alert_rule,
)


def _get_alert_rule_by_name(user_id: str, rule_name: str, *, db: Session) -> AlertRule | None:
    """
    Busca una regla de alerta por nombre (case-insensitive) del usuario

    Args:
        user_id(str): ID del usuario
        rule_name(str): Nombre de la regla
        db(Session): Sesión de BD

    Returns:
        AlertRule | None: Regla encontrada o None
    """
    return db.query(AlertRule).filter(
        AlertRule.user_id == user_id,
        AlertRule.name.ilike(rule_name.strip()),
    ).first()


def validate_alert_rule_dsl(
        user_id: str,
        rule_dsl: dict[str, Any]
) -> dict[str, Any]:
    """
    Valida y normaliza una regla en formato DSL (Domain-Specific Language)

    Args:
        user_id(str): Identificador del usuario
        rule_dsl(dict[str, Any]): Regla en formato DSL

    Returns:
        dict[str, Any]: Resultado de validación (valid/issues) y regla normalizada si aplica
    """

    issues: list[dict[str, Any]] = []

    try:
        parsed = AlertRuleDSL.model_validate(rule_dsl)
    except ValidationError as e:
        for error in e.errors():
            issues.append(
                {
                    "field": ".".join(str(err) for err in error.get("loc", [])),
                    "code": error.get("type", "validation_error"),
                    "message": error.get("msg", "invalid"),
                    "severity": "error",
                }
            )
        return {"valid": False, "issues": issues, "requires_confirmation": False, "reason": ""}

    requires_confirmation = False
    reason = ""

    scope_all = parsed.scope.target_type == "all"
    external = any(channel.kind in ("email", "webhook") for channel in parsed.channels)
    very_frecuent = parsed.schedule.frequency == "hourly"
    if scope_all and external and very_frecuent:
        requires_confirmation = True
        reason = "Impacto alto: scope=all + canal externo + evaluación hourly"

    normalized = parsed.model_dump()
    if parsed.schedule.frequency in ("daily", "weekly") and not parsed.schedule.at_time:
        normalized["schedule"]["at_time"] = "09:00"

    return {
        "valid": True,
        "normalized_rule": normalized,
        "issues": [],
        "requires_confirmation": requires_confirmation,
        "reason": reason,
    }


def resolve_scope(
        user_id: str,
        scope: dict[str, Any],
        *,
        db: Session,
) -> dict[str, Any]:
    """
    Resuelve el alcance (scope) a una lista concreta de domain_ids

    Args:
        user_id(str): Identificador del usuario
        scope(dict[str, Any]): Scope declarado (all/domains/tags)
        db(Session): Sesión de base de datos

    Returns:
        dict[str, Any]: Scope resuelto con target_type, domain_ids y estadísticas básicas
    """

    target_type = (scope.get("target_type") or "domains").strip().lower()

    if target_type == "all":
        return {"target_type": "all", "domain_ids": [], "missing_domains": []}

    if target_type == "domains":
        domains = scope.get("domains") or []
        domain_ids = scope.get("domain_ids") or []

        if domain_ids:
            return {"target_type": "domains", "domain_ids": domain_ids, "missing_domains": []}

        if not domains:
            return {"error": "invalid_scope", "message": "scope.domains o scope.domains_ids requerido"}

        wanted = [domain.strip().lower() for domain in domains if isinstance(domain, str) and domain.strip()]
        if not wanted:
            return {"error": "invalid_scope", "message": "scope.domains vacío"}

        rows = db.execute(
            select(Domain).where(Domain.user_id == user_id, Domain.domain_name.in_(wanted))
        ).scalars().all()

        found_map = {domain.domain_name.lower(): domain.id for domain in rows if getattr(domain, "domain_name", None)}
        missing = [name for name in wanted if name not in found_map]
        resolved_ids = [found_map[name] for name in wanted if name in found_map]

        return {
            "target_type": "domains",
            "domain_ids": resolved_ids,
            "missing_domains": missing,
            "stats": {"matched_domains": len(resolved_ids)}
        }

    if target_type == "tags":
        tags = scope.get("tags") or []
        wanted_tags = {tag.strip().lower() for tag in tags if isinstance(tag, str) and tag.strip()}

        if not wanted_tags:
            return {"error": "invalid_scope", "message": "scope.tags vacío"}

        rows = db.execute(
            select(Domain).where(Domain.user_id == user_id, Domain.status == "activo")
        ).scalars().all()

        matched_ids: list[str] = []

        for row in rows:
            d_tags = getattr(row, "tags", None) or []
            if isinstance(d_tags, str):
                d_tags = [d_tags]

            d_tags_norm = {str(x).strip().lower() for x in d_tags if x is not None and str(x).strip()}
            if wanted_tags.intersection(d_tags_norm):
                matched_ids.append(row.id)

        return {
            "target_type": "domains",
            "domain_ids": matched_ids,
            "missing_domains": [],
            "stats": {"matched_domains": len(matched_ids)},
        }

    return {"error": "validation_failed", "message": "scope.target_type inválido", }


def upsert_alert_rule(
        user_id: str,
        rule_dsl: dict[str, Any],
        mode: str = "create",
        rule_id: str | None = None,
        *,
        db: Session,
) -> dict[str, Any]:
    """
    Crea una regla de alerta en base de datos a partir del DSL

    Args:
        user_id(str): Identificador del usuario
        rule_dsl(dict[str, Any]): Regla en formato DSL
        mode(str): Modo de operación (create/update/upsert)
        rule_id(str | None): Identificador de regla para update/upsert (si aplica)
        db(Session): Sesión de base de datos

    Returns:
        dict[str, Any]: Datos de la regla creada (rule_id, versión y flags)
    """

    new_id = f"rule_{uuid.uuid4().hex[:8]}"
    name = rule_dsl.get("rule_name") or rule_dsl.get("name") or "Regla"
    rule_type = rule_dsl.get("rule_type", "risk")
    severity = rule_dsl.get("severity", "medium")
    enabled = bool(rule_dsl.get("enabled", True))

    logic_json = {
        "dsl_version": rule_dsl.get("dsl_version", "v1.0"),
        "rule_type": rule_type,
        "scope": rule_dsl.get("scope", {}),
        "condition": rule_dsl.get("condition", {}),
        "channels": rule_dsl.get("channels", []),
        "cooldown": rule_dsl.get("cooldown", {}),
        "dedup": rule_dsl.get("dedup", {}),
        "metadata": rule_dsl.get("metadata", {}),
    }

    schedule_json = rule_dsl.get("schedule", {})

    row = AlertRule(
        id=new_id,
        user_id=user_id,
        name=name,
        rule_type=rule_type,
        severity=severity,
        is_enabled=enabled,
        version=1,
        logic_json=logic_json,
        schedule_json=schedule_json,
    )

    db.add(row)
    db.flush()

    return {"rule_id": new_id, "version": 1, "created": True, }


def set_rule_targets(
        user_id: str,
        rule_id: str,
        session_id: str,
        resolved_scope: dict[str, Any] | None = None,
        *,
        db: Session,
) -> dict[str, Any]:
    """
    Asocia una regla a sus dominios objetivo, reemplazando los targets previos

    Args:
        user_id(str): Identificador del usuario
        rule_id(str): Identificador de la regla
        session_id(str): Identificador de sesion
        resolved_scope(dict[str, Any]) Opcional: Scope resuelto con domain_ids
        db(Session): Sesión de base de datos

    Returns:
        dict[str, Any]: Resumen de targets asociados
    """
    if resolved_scope is None:
        draft = get_rule_draft(user_id, session_id)
        resolved_scope = draft.get("resolved_scope") or (draft.get("normalized_rule") or {}).get("scope")

        # fallback adicional: si guardaste normalized_rule.scope ya resuelta
        if not resolved_scope:
            normalized_rule = draft.get("normalized_rule") or {}
            resolved_scope = normalized_rule.get("scope")

    if not resolved_scope:
        return {
            "error": "missing_resolved_scope",
            "message": "resolved_scope no proporcionado y no se encontró en el draft (resolved_scope/normalized_rule.scope).",   # noqa: E501
        }

    domain_ids = resolved_scope.get("domain_ids", [])

    # limpia targets previos
    db.execute(delete(AlertRuleTarget).where(AlertRuleTarget.rule_id == rule_id))

    for dom_id in domain_ids:
        db.add(AlertRuleTarget(rule_id=rule_id, domain_id=dom_id))

    db.flush()

    return {"attached": {"target_type": "domains", "domain_ids_count": len(domain_ids)}, }


def register_rule_schedule(
        user_id: str,
        rule_id: str,
        session_id: str,
        schedule: dict[str, Any] | None = None,
        *,
        db: Session,
) -> dict[str, Any]:
    """
    Registra un job de scheduling para una regla

    Args:
        user_id(str): Identificador del usuario
        rule_id(str): Identificador de la regla
        session_id(str): Identificador de la sesión
        schedule(dict[str, Any]) Opcional: Configuración de schedule (frecuencia/horario/etc.)
        db(Session): Sesión de base de datos

    Returns:
        dict[str, Any]: Datos del job creado (job_id y próxima ejecución)
    """

    if schedule is None:
        draft = get_rule_draft(user_id, session_id)
        normalized_rule = draft.get("normalized_rule") or {}
        schedule = normalized_rule.get("schedule") or draft.get("schedule")

    if not schedule:
        return {
            "error": "missing_schedule",
            "message": "schedule no proporcionado y no se encontró en el draft (normalized_rule.schedule / draft.schedule).",   # noqa: E501
        }

    freq = schedule.get("frequency")
    if not isinstance(freq, str) or not freq.strip():
        return {
            "error": "invalid_schedule",
            "message": "schedule.frequency es obligatorio.",
            "schedule_received": schedule,
        }

    job_id = f"job_{uuid.uuid4().hex[:8]}"

    row = ScheduleJob(
        id=job_id,
        user_id=user_id,
        rule_id=rule_id,
        schedule_json=schedule,
        status="activo",
        next_run_at=None,
    )

    db.add(row)
    db.flush()

    return {"job_id": job_id, "next_run_at": "mock_next_run", }


def list_alert_rules_tool(user_id: str, *, db: Session) -> dict[str, Any]:
    """
    Lista todas las reglas de alerta del usuario

    Args:
        user_id(str): ID del usuario
        db(Session): Sesión de BD

    Returns:
        dict[str, Any]: Items con count
    """
    return list_alert_rules(user_id=user_id, db=db)


def delete_alert_rule_tool(user_id: str, rule_name: str, *, db: Session) -> dict[str, Any]:
    """
    Elimina una regla de alerta del usuario por nombre

    Args:
        user_id(str): ID del usuario
        rule_name(str): Nombre de la regla a eliminar
        db(Session): Sesión de BD

    Returns:
        dict[str, Any]: Resultado con deleted=True/False
    """
    rule = _get_alert_rule_by_name(user_id, rule_name, db=db)

    if not rule:
        return {"deleted": False, "error": f"La alerta '{rule_name}' no existe o no te pertenece."}

    return delete_alert_rule(rule_id=rule.id, user_id=user_id, db=db)


def toggle_alert_rule_tool(user_id: str, rule_name: str, enabled: bool, *, db: Session) -> dict[str, Any]:
    """
    Activa o pausa una regla de alerta del usuario por nombre

    Args:
        user_id(str): ID del usuario
        rule_name(str): Nombre de la regla
        enabled(bool): True para activar, False para pausar
        db(Session): Sesión de BD

    Returns:
        dict[str, Any]: Resultado con updated=True/False
    """
    rule = _get_alert_rule_by_name(user_id, rule_name, db=db)

    if not rule:
        return {"updated": False, "error": f"La alerta '{rule_name}' no existe o no te pertenece."}

    return toggle_alert_rule(rule_id=rule.id, user_id=user_id, enabled=enabled, db=db)
