from __future__ import annotations
from typing import Literal, Union
from pydantic import BaseModel, Field
from app.core.settings import settings


class Scope(BaseModel):
    """ Define el alcance de la regla: todos los dominios, dominios específicos o por etiquetas. """
    target_type: Literal["all", "domains", "tags"]
    domain_ids: list[str] | None = None
    tags: list[str] | None = None


class RiskCondition(BaseModel):
    """ Condición basada en nivel, puntuación o variación de riesgo dentro de una ventana de tiempo. """
    kind: Literal["risk"] = "risk"
    risk_level_gte: Literal["low", "medium", "high", "critical"] | None = None
    risk_score_gte: int | None = Field(default=None, ge=0, le=100)
    risk_delta_gte: int | None = Field(default=None, ge=0, le=100)
    windows_hours: int = Field(default=24, ge=1, le=720)


class ExpiryCondition(BaseModel):
    """ Condición basada en la proximidad a la fecha de expiración del dominio. """
    kind: Literal["expiry"] = "expiry"
    days_before: int = Field(..., ge=1, le=365)
    only_if_auto_renew_off: bool = False


# tipo de condicion riesgo y/o condición
Condition = Union[RiskCondition, ExpiryCondition]


class Schedule(BaseModel):
    """ Define la frecuencia y el horario de ejecución de la regla. """

    frequency: Literal["hourly", "daily", "weekly"]
    at_time: str | None = Field(default=None, description="HH:MM (requerido para daily/weekly)")
    timezone: str = settings.default_timezone

    # Mejora pendiente - days_of_week no se recoge en el flujo conversacional
    # Implementar extractor en extractors.py y pregunta en questions.py (CU-03)
    days_of_week: list[Literal["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]] | None = None


class Channel(BaseModel):
    """ Canal de notificación y configuración de envío. """

    kind: Literal["email", "webhook", "in_app"]
    to: str | None = None
    template: Literal["default", "executive", "technical"] = "default"


class Cooldown(BaseModel):
    """ Tiempo mínimo de espera entre notificaciones para evitar alertas repetidas
    Mejora pendiente - cooldown siempre usa el valor por defecto (24h, per_domain=True)
    Implementar configuración en el flujo conversacional del CU-03
    cooldown: Cooldown = Field(default_factory=Cooldown)"""

    hours: int = Field(default=24, ge=0, le=720)
    per_domain: bool = True


class AlertRuleDSL(BaseModel):
    """ Definición completa de una regla de alerta en formato DSL. """

    dsl_version: str = Field(default="v1.0")
    rule_name: str = Field(..., min_length=3, max_length=80)
    description: str | None = Field(default=None, max_length=240)

    # rule_type: Literal["risk", "expiry"]
    rule_type: Literal["expiry"]
    enabled: bool = True
    severity: Literal["low", "medium", "high"] = "medium"

    scope: Scope
    condition: Condition
    schedule: Schedule
    channels: list[Channel] = Field(..., min_length=1, max_length=5)
    cooldown: Cooldown = Field(default_factory=Cooldown)
