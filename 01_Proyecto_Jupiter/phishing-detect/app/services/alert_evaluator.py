from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models import AlertEvent, AlertRule, AlertRuleTarget, Domain, DomainEnrichment

logger = get_logger("alert_evaluator")


def _cooldown_ok(rule_id: str, domain_id: str, cooldown_hours: int, *, db: Session) -> bool:
    """
    Comprueba si ha pasado el tiempo de cooldown desde la última alerta enviada

    Args:
        rule_id(str): Identificador de la regla
        domain_id(str): Identificador del dominio
        cooldown_hours(int): Horas mínimas entre alertas (está predeterminado a 24 horas)
        db(Session): Sesión de base de datos

    Returns:
        bool: True si puede enviarse la alerta, False si aún está en cooldown
    """
    if cooldown_hours <= 0:
        return True

    since = datetime.now(timezone.utc) - timedelta(hours=cooldown_hours)
    last = db.execute(
        select(AlertEvent)
        .where(
            AlertEvent.rule_id == rule_id,
            AlertEvent.domain_id == domain_id,
            AlertEvent.sent == True,  # noqa: E712
            AlertEvent.triggered_at >= since,
        )
        .limit(1)
    ).scalar_one_or_none()
    return last is None


def evaluate_rule(rule: AlertRule, *, db: Session) -> list[dict[str, Any]]:
    """
    Evalúa una regla contra todos sus dominios objetivo.

    Args:
        rule(AlertRule): Regla de alerta a evaluar
        db(Session): Sesión de base de datos

    Returns:
        list[dict[str, Any]]: Dominios que cumplen la condición y superan el cooldown
    """
    logic = rule.logic_json or {}
    condition = logic.get("condition", {})
    cooldown_cfg = logic.get("cooldown", {})
    cooldown_hours = cooldown_cfg.get("hours", 24) if isinstance(cooldown_cfg, dict) else 24
    rule_type = logic.get("rule_type", rule.rule_type)

    targets = db.execute(
        select(AlertRuleTarget).where(AlertRuleTarget.rule_id == rule.id)
    ).scalars().all()

    if not targets:
        return []

    triggered: list[dict[str, Any]] = []

    for target in targets:
        domain = db.get(Domain, target.domain_id)
        if not domain:
            continue

        enrichment = db.execute(
            select(DomainEnrichment).where(DomainEnrichment.domain_id == domain.id)
        ).scalar_one_or_none()

        if not enrichment:
            continue

        matched = False
        details: dict[str, Any] = {}

        if rule_type == "expiry":
            days_before = condition.get("days_before") or condition.get("days_before_expiry")
            exp = enrichment.whois_expiration_date
            if days_before and exp:
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                days_left = (exp - datetime.now(timezone.utc)).days
                if 0 <= days_left <= int(days_before):
                    matched = True
                    details = {
                        "days_left": days_left,
                        "expiration_date": exp.date().isoformat(),
                        "threshold_days": days_before,
                    }

        if matched and _cooldown_ok(rule.id, domain.id, cooldown_hours, db=db):
            triggered.append({
                "domain_id": domain.id,
                "domain_name": domain.domain_name,
                "rule_type": rule_type,
                "details": details,
            })

    return triggered
