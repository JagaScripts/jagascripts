from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.core.logging import get_logger
from app.db.models import AlertEvent, AlertRule, ScheduleJob
from app.db.session import SessionLocal
from app.services.alert_evaluator import evaluate_rule
from app.services.notifier import send_notification

logger = get_logger("scheduler")


def run_daily_alerts() -> dict[str, Any]:
    """
    Evalúa todas las reglas activas y envía notificaciones. Se ejecuta diariamente a las 06:00 UTC

    Returns:
        dict[str, Any]: Resumen con rules_evaluated y alerts_sent
    """
    logger.info(
        "Iniciando evaluación diaria de alertas",
        extra={"event": "scheduler_run_start"},
    )

    total_sent = 0
    rules_count = 0

    try:
        with SessionLocal() as db:
            rules = db.execute(
                select(AlertRule).where(AlertRule.is_enabled == True)  # noqa: E712
            ).scalars().all()

            for rule in rules:
                schedule = rule.schedule_json or {}
                frequency = schedule.get("frequency", "daily")

                # Reglas semanales: solo ejecutar si hoy es el día configurado
                if frequency == "weekly":
                    days_of_week = schedule.get("days_of_week")
                    if days_of_week:
                        day_map = {
                            "monday": "lunes", "tuesday": "martes",
                            "wednesday": "miercoles", "thursday": "jueves",
                            "friday": "viernes", "saturday": "sabado",
                            "sunday": "domingo",
                        }
                        today_es = day_map.get(
                            datetime.now(timezone.utc).strftime("%A").lower(), ""
                        )
                        if today_es not in days_of_week:
                            continue

                try:
                    rules_count += 1
                    triggered = evaluate_rule(rule, db=db)
                    if not triggered:
                        continue

                    logic = rule.logic_json or {}
                    channels = logic.get("channels", [])

                    for channel in channels:
                        result = send_notification(
                            channel=channel,
                            rule_name=rule.name,
                            user_id=rule.user_id,
                            triggered_domains=triggered,
                        )

                        for domain_info in triggered:
                            event = AlertEvent(
                                id=f"ev_{uuid.uuid4().hex[:12]}",
                                rule_id=rule.id,
                                domain_id=domain_info["domain_id"],
                                user_id=rule.user_id,
                                triggered_at=datetime.now(timezone.utc),
                                channel_kind=channel.get("kind", "unknown"),
                                sent=result.get("sent", False),
                                error=result.get("error"),
                                payload_json={
                                    "rule_name": rule.name,
                                    "domain_name": domain_info["domain_name"],
                                    "details": domain_info["details"],
                                },
                            )
                            db.add(event)
                            total_sent += 1

                except Exception as e:
                    logger.error(
                        f"Error evaluando regla {rule.id}",
                        extra={"event": "scheduler_rule_error", "rule_id": rule.id, "error": str(e)},
                        exc_info=True,
                    )

            # Actualizar last_run_at en todos los jobs activos
            now = datetime.now(timezone.utc)
            jobs = db.execute(
                select(ScheduleJob).where(ScheduleJob.status == "activo")
            ).scalars().all()
            for job in jobs:
                job.last_run_at = now

            db.commit()

    except Exception as e:
        logger.error(
            f"Error en el scheduler diario: {e}",
            extra={"event": "scheduler_run_error"},
            exc_info=True,
        )

    summary = {"rules_evaluated": rules_count, "alerts_sent": total_sent}
    logger.info(
        "Evaluación diaria completada",
        extra={"event": "scheduler_run_end", "total_sent": total_sent},
    )
    return summary


def create_scheduler() -> BackgroundScheduler:
    """
    Crea y configura el scheduler con el job diario de alertas a las 06:00 UTC.

    Returns:
        BackgroundScheduler: Scheduler configurado y listo para arrancar
    """
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_daily_alerts,
        CronTrigger(hour=6, minute=0, timezone="UTC"),
        id="daily_alerts",
        name="Evaluación diaria de alertas",
        replace_existing=True,
    )
    return scheduler
