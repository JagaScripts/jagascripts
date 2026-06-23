from __future__ import annotations

from fastapi import APIRouter

from app.sheduler import run_daily_alerts

router = APIRouter()


@router.post("/alerts/run")
def trigger_alerts() -> dict:
    """
    Dispara manualmente la evaluación diaria de alertas

    Returns:
        dict: Resumen con reglas evaluadas y alertas enviadas
    """
    summary = run_daily_alerts()
    return {"status": "ok", **summary}
