from __future__ import annotations

import dns.resolver

from typing import Any
from app.core.logging import get_logger

logger = get_logger("mxrecord_client")


def get_mx_records(domain_name: str) -> list[dict[str, Any]]:
    """
    Obtiene registros MX (servidores de correo) de un dominio

    Args:
        domain_name (str): Nombre del dominio

    Returns:
        list[dict]: Lista de MX records con priority y exchange
                   [{"priority": 10, "exchange": "mail.example.com"}, ...]
    """
    result = []

    try:
        answers = dns.resolver.resolve(domain_name, "MX")
        for mx in answers:
            result.append({
                "priority": int(mx.preference),
                "exchange": str(mx.exchange).rstrip("."),
            })
        # Ordenar por prioridad
        result.sort(key=lambda x: x["priority"])
    except Exception as e:
        logger.debug(f"No MX records para {domain_name}: {e}")

    return result
