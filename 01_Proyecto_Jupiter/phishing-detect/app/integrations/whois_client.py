from __future__ import annotations

import whois
from datetime import datetime, timezone
from typing import Any

from app.core.logging import get_logger

logger = get_logger("whois_client")


def get_whois_data(domain_name: str) -> dict[str, Any]:
    """
    Obtiene datos WHOIS de un dominio

    Args:
        domain_name (str): Nombre del dominio

    Returns:
        dict: Datos WHOIS con registrante, registrante, fecha_caducidad, fecha_alta
              o dict vacío si falla.
    """
    try:
        whois_info = whois.whois(domain_name)

        expiration = whois_info.expiration_date
        if isinstance(expiration, list) and expiration:
            expiration = expiration[0]
        expiration_date = expiration if isinstance(expiration, datetime) else None

        creation = whois_info.creation_date
        if isinstance(creation, list) and creation:
            creation = creation[0]
        creation_date = creation if isinstance(creation, datetime) else None

        return {
            "registrar": whois_info.registrar or None,
            "registrant": whois_info.registrant_name or whois_info.name or None,
            "expiration_date": expiration_date.replace(tzinfo=timezone.utc) if expiration_date else None,
            "creation_date": creation_date.replace(tzinfo=timezone.utc) if creation_date else None,
        }
    except Exception as e:
        logger.error(
            "Error en WHOIS lookup",
            extra={"event": "whois_error", "domain": domain_name, "error": str(e)},
            exc_info=True,
        )
        return {}
