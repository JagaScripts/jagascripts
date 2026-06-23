from __future__ import annotations

from typing import Any
from datetime import datetime, timezone

from app.core.logging import get_logger, log_event
from app.integrations.reputation.virustotal import VirusTotalProvider

logger = get_logger("reputation_service")


def check_domain_reputation(domain_name: str) -> dict[str, Any]:
    """
    Verifica la reputación de distintas fuentes (ahora solo VirusTotal)

    Args:
        domain_name(str): Nombre del dominio

    Returns:
        dict[str, Any]: Datos de reputación del dominio
    """
    try:
        log_event(
            logger,
            level=20,
            event="reputation_check_start",
            message="Verificando reputación",
            extra={"domain": domain_name},
        )

        providers_data = {}
        risk_scores = []

        # VirusTotal
        vt_provider = VirusTotalProvider()
        vt_result = vt_provider.check_reputation(domain_name)
        providers_data["virustotal"] = vt_result

        if vt_result.get("error") is None:
            risk_scores.append(vt_result.get("risk_score", 0))

        # Calcular valor del score más alto
        max_score = max(risk_scores) if risk_scores else 0.0

        result = {
            "domain_name": domain_name,
            "providers": providers_data,
            "max_risk_score": max_score,
            "checked_at": datetime.now(timezone.utc).strftime("%d/%m/%Y_%H:%M:%S"),
            "error": None,
        }

        log_event(
            logger,
            level=20,
            event="reputation_check_complete",
            message="Reputación verificada",
            extra={"domain": domain_name, "score": max_score},
        )
        return result

    except Exception as e:
        log_event(
            logger,
            level=40,
            event="reputation_check_error",
            message="Error verificando reputación",
            extra={"domain": domain_name, "error": str(e)},
            exc_info=True,
        )
        return {
            "domain_name": domain_name,
            "providers": {},
            "max_risk_score": 0.0,
            "checked_at": datetime.now(timezone.utc).strftime("%d/%m/%Y_%H:%M:%S"),
            "error": str(e),
        }
