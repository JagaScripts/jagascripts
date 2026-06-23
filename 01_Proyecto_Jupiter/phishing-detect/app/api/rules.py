from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.db.deps import get_db
from app.db.models import Domain, AlertRule, AlertRuleTarget, ScheduleJob

router = APIRouter()


class RuleChannel(BaseModel):
    kind: str
    to: str | None = None


class RuleSchedule(BaseModel):
    frequency: str
    at_time: str | None = None
    timezone: str | None = None


class RuleCooldown(BaseModel):
    seconds: int = 0


class RuleScope(BaseModel):
    target_type: str = Field(..., description="all|domains|tags")
    domains: list[str] = Field(default_factory=list, description="Opcional: nombres de dominio")
    domain_ids: list[str] = Field(default_factory=list, description="Opcional: ids de dominio")
    tags: list[str] = Field(default_factory=list, description="Opcional: tags")


class AlertRuleRead(BaseModel):
    id: str
    user_id: str
    name: str | None = None
    rule_type: str
    is_enabled: bool = True

    condition: dict[str, Any] = Field(default_factory=dict)
    scope: RuleScope = Field(default_factory=lambda: RuleScope(target_type="domains"))
    channels: list[RuleChannel] = Field(default_factory=list)
    schedule: RuleSchedule | None = None
    cooldown: RuleCooldown | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None


class AlertRuleListResponse(BaseModel):
    items: list[AlertRuleRead] = Field(default_factory=list)
    count: int


def _load_rule_targets(db: Session, rule_id: str) -> list[AlertRuleTarget]:
    return db.execute(
        select(AlertRuleTarget).where(AlertRuleTarget.rule_id == rule_id)
    ).scalars().all()


def _load_domains_by_ids(db: Session, user_id: str, domain_ids: list[str]) -> list[Domain]:
    if not domain_ids:
        return []
    return db.execute(
        select(Domain).where(Domain.user_id == user_id, Domain.id.in_(domain_ids))
    ).scalars().all()


def _load_schedule(db: Session, rule_id: str) -> ScheduleJob | None:
    return db.execute(
        select(ScheduleJob).where(ScheduleJob.rule_id == rule_id)
    ).scalars().first()


def _to_read_model(db: Session, rule: AlertRule) -> AlertRuleRead:
    # 1) targets → scope
    targets = _load_rule_targets(db, rule.id)
    domain_ids = [t.domain_id for t in targets if getattr(t, "domain_id", None)]

    domains = _load_domains_by_ids(db, rule.user_id, domain_ids)
    domain_names = [d.domain_name for d in domains if getattr(d, "domain_name", None)]

    scope = RuleScope(
        target_type="domains" if domain_ids else "all",
        domain_ids=domain_ids,
        domains=domain_names,
        tags=[],
    )

    # 2) schedule
    sch = _load_schedule(db, rule.id)
    schedule = None
    if sch is not None:
        schedule = RuleSchedule(
            frequency=getattr(sch, "frequency", "daily"),
            at_time=getattr(sch, "at_time", None),
            timezone=getattr(sch, "timezone", None),
        )

    # 3) channels / condition / cooldown
    condition = getattr(rule, "condition", {}) or {}
    channels_raw = getattr(rule, "channels", []) or []
    cooldown_raw = getattr(rule, "cooldown", None)

    channels: list[RuleChannel] = []
    for ch in channels_raw:
        if isinstance(ch, dict):
            channels.append(RuleChannel(kind=ch.get("kind", "unknown"), to=ch.get("to")))
        else:
            # fallback defensivo
            channels.append(RuleChannel(kind="unknown", to=None))

    cooldown = None
    if isinstance(cooldown_raw, dict):
        cooldown = RuleCooldown(seconds=int(cooldown_raw.get("seconds", 0)))
    elif isinstance(cooldown_raw, int):
        cooldown = RuleCooldown(seconds=cooldown_raw)

    return AlertRuleRead(
        id=rule.id,
        user_id=rule.user_id,
        name=getattr(rule, "name", None),
        rule_type=rule.rule_type,
        is_enabled=getattr(rule, "is_enabled", True),
        condition=condition,
        scope=scope,
        channels=channels,
        schedule=schedule,
        cooldown=cooldown,
        created_at=getattr(rule, "created_at", None),
        updated_at=getattr(rule, "updated_at", None),
    )


@router.get("/rules", response_model=AlertRuleListResponse)
def list_rules(
    user_id: str = Query(..., min_length=1, max_length=80),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    rule_type: str | None = Query(None, description="Filtra por 'expiry' o 'risk'"),
    is_enabled: bool | None = Query(None),
    db: Session = Depends(get_db),
) -> AlertRuleListResponse:
    stmt = select(AlertRule).where(AlertRule.user_id == user_id)

    if rule_type:
        stmt = stmt.where(AlertRule.rule_type == rule_type)
    if is_enabled is not None:
        stmt = stmt.where(AlertRule.is_enabled == is_enabled)

    stmt = stmt.order_by(desc(AlertRule.created_at)).limit(limit).offset(offset)

    rules = db.execute(stmt).scalars().all()
    items = [_to_read_model(db, r) for r in rules]

    return AlertRuleListResponse(items=items, count=len(items))


@router.get("/rules/{rule_id}", response_model=AlertRuleRead)
def get_rule(
    rule_id: str,
    user_id: str = Query(..., min_length=1, max_length=80),
    db: Session = Depends(get_db),
) -> AlertRuleRead:
    rule = db.execute(
        select(AlertRule).where(AlertRule.id == rule_id, AlertRule.user_id == user_id)
    ).scalars().first()

    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    return _to_read_model(db, rule)
