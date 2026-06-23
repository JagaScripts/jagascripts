from __future__ import annotations
from datetime import datetime, timezone, timedelta
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class Domain(Base):
    """ Tabla/Modelo de dominio monitorizado por un usuario, con estado y etiquetas de clasificación. """

    __tablename__ = "domains"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(80), index=True)
    domain_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="activo")  # solo acepta activo o inactivo
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_domains_user_status", "user_id", "status"),
    )


class AlertRule(Base):
    """Regla de alerta configurable (lógica + schedule) asociada a un usuario y a un conjunto de dominios objetivo."""

    __tablename__ = "alert_rules"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(80), index=True)

    name: Mapped[str] = mapped_column(String(80))
    rule_type: Mapped[str] = mapped_column(String(30))
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    version: Mapped[int] = mapped_column(Integer, default=1)
    logic_json: Mapped[dict] = mapped_column(JSONB)
    schedule_json: Mapped[dict] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(
        timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    targets: Mapped[list["AlertRuleTarget"]] = relationship(
        back_populates="rule", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_rules_user_enabled", "user_id", "is_enabled"),
        Index("idx_rules_user_type", "user_id", "rule_type"),
    )


class AlertRuleTarget(Base):
    """ Relación entre una regla de alerta y los dominios a los que aplica. """

    __tablename__ = "alert_rule_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_id: Mapped[str] = mapped_column(String(80), ForeignKey("alert_rules.id", ondelete="CASCADE"), index=True)
    domain_id: Mapped[str] = mapped_column(String(80), ForeignKey("domains.id"), index=True)

    rule: Mapped["AlertRule"] = relationship(back_populates="targets")

    __table_args__ = (
        UniqueConstraint("rule_id", "domain_id", name="uq_rule_domain"),
    )


class ScheduleJob(Base):
    """ Job de ejecución programada de una regla, con estado y próxima ejecución. """

    __tablename__ = "schedules"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(80), index=True)
    rule_id: Mapped[str] = mapped_column(String(80), ForeignKey("alert_rules.id", ondelete="CASCADE"), index=True)

    schedule_json: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default="activo")  # solo acepta activo o inactivo

    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_sched_user_status", "user_id", "status"),
    )


class DomainEnrichment(Base):
    """Datos de enriquecimiento: WHOIS, DNS, MX, reputación"""
    __tablename__ = "domain_enrichment"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    domain_id: Mapped[str] = mapped_column(String(80), ForeignKey(
        "domains.id", ondelete="CASCADE"), unique=True, index=True)

    # WHOIS
    whois_registrar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    whois_expiration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    whois_creation_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    whois_registrant: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # DNS
    dns_a_records: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    dns_ns_records: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    dns_cname_records: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    # MX
    mx_servers: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)

    # Reputación - VirusTotal
    virustotal_malicioso: Mapped[int | None] = mapped_column(Integer, nullable=True)
    virustotal_sospechoso: Mapped[int | None] = mapped_column(Integer, nullable=True)
    virustotal_ultima_comprobacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Score calculado en backend (0-100)
    reputation_score: Mapped[float] = mapped_column(default=0.0, index=True)

    # Metadata
    last_enriched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    last_enrichment_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    enrichment_version: Mapped[str] = mapped_column(String(10), default="v1")
    enrichment_status: Mapped[str] = mapped_column(String(20), default="pending", index=True)


class AlertEvent(Base):
    """Registro de cada alerta disparada: condición detectada + resultado del envío"""
    __tablename__ = "alert_events"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    rule_id: Mapped[str] = mapped_column(String(80), ForeignKey("alert_rules.id", ondelete="CASCADE"), index=True)
    domain_id: Mapped[str] = mapped_column(String(80), ForeignKey("domains.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(80), index=True)

    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    channel_kind: Mapped[str] = mapped_column(String(20))
    sent: Mapped[bool] = mapped_column(Boolean, default=False)
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    payload_json: Mapped[dict] = mapped_column(JSONB)

    __table_args__ = (
        Index("idx_alert_events_rule_domain", "rule_id", "domain_id"),
        Index("idx_alert_events_user", "user_id", "triggered_at"),
    )


class DomainAnalysisCache(Base):
    """ Caché de análisis de phishing """

    __tablename__ = "domain_analysis_cache"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    domain_analyzed: Mapped[str] = mapped_column(String(255), index=True)

    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(20))

    target_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_similarity: Mapped[float | None] = mapped_column(nullable=True)

    indicators_json: Mapped[list] = mapped_column(JSONB, default=list)
    whois_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    dns_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    mx_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    virustotal_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=24),
        index=True,
    )

    history_entries: Mapped[list["UserAnalysisHistory"]] = relationship(
        back_populates="cache_entry", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_analysis_cache_domain_expires", "domain_analyzed", "expires_at"),
    )


class UserAnalysisHistory(Base):
    """ Historial de análisis por usuario. Está referenciada a la caché de análisis """

    __tablename__ = "user_analysis_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(80), index=True)

    input_raw: Mapped[str] = mapped_column(String(500))
    input_type: Mapped[str] = mapped_column(String(20))  # url, domain o email

    cache_id: Mapped[str] = mapped_column(
        String(80), ForeignKey("domain_analysis_cache.id", ondelete="CASCADE"), index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    cache_entry: Mapped["DomainAnalysisCache"] = relationship(back_populates="history_entries")

    __table_args__ = (
        Index("idx_history_user_created", "user_id", "created_at"),
    )


class AuditLog(Base):
    """Registro de auditoría de eventos del sistema"""
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts_utc: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    trace_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    user_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    event: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
