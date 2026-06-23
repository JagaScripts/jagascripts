from __future__ import annotations

from typing import Any
from datetime import datetime, timezone

from app.core.logging import get_logger
from app.integrations.whois_client import get_whois_data
from app.integrations.dns_client import get_dns_records
from app.integrations.mx_client import get_mx_records

logger = get_logger("domain_analysis_service")


def analyze_domain(domain_name: str) -> dict[str, Any]:
    """
    Analiza un dominio obteniendo datos de WHOIS, DNS y MX

    Args:
        domain_name(str): Nombre del dominio

    Returns:
        dict[str, Any]: Resultados del análisis
    """
    try:
        logger.info(
            f"Iniciando análisis del dominio: {domain_name}",
            extra={"event": "domain_analysis_start", "domain": domain_name},
        )

        whois_data = get_whois_data(domain_name)
        dns_data = get_dns_records(domain_name)
        mx_data = get_mx_records(domain_name)

        result = {
            "domain_name": domain_name,
            "whois": whois_data,
            "dns": dns_data,
            "mx": mx_data,
            "analyzed_at": datetime.now(timezone.utc).strftime("%d/%m/%Y_%H:%M:%S"),
            "error": None,
        }

        logger.info(
            f"Análisis completado para {domain_name}",
            extra={"event": "domain_analysis_complete", "domain": domain_name},
        )

        return result

    except Exception as e:
        logger.error(
            f"Error analizando {domain_name}",
            extra={"event": "domain_analysis_error", "domain": domain_name, "error": str(e)},
            exc_info=True,
        )
        return {
            "domain_name": domain_name,
            "whois": {},
            "dns": {},
            "mx": [],
            "analyzed_at": datetime.now(timezone.utc).strftime("%d/%m/%Y_%H:%M:%S"),
            "error": str(e),
        }
