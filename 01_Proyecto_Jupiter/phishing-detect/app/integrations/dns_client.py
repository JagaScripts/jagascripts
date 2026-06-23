from __future__ import annotations

import dns.resolver
from typing import Any

from app.core.logging import get_logger

logger = get_logger("dns_client")


def get_dns_records(domain_name: str) -> dict[str, Any]:
    """
    Obtiene registros DNS (A, NS, CNAME) de un dominio

    Args:
        domain_name (str): Nombre del dominio

    Returns:
        dict: Registros DNS con a_records, ns_records, cname_records
    """
    result = {
        "a_records": [],
        "ns_records": [],
        "cname_records": [],
    }

    # A Records
    try:
        answers = dns.resolver.resolve(domain_name, "A")
        result["a_records"] = [str(rdata) for rdata in answers]
    except Exception as e:
        logger.warning(
            f"No A records para {domain_name}",
            extra={"event": "dns_a_error", "domain": domain_name, "error": str(e)},
        )

    # NS Records
    try:
        answers = dns.resolver.resolve(domain_name, "NS")
        result["ns_records"] = [str(rdata) for rdata in answers]
    except Exception as e:
        logger.warning(
            f"No NS records para {domain_name}",
            extra={"event": "dns_ns_error", "domain": domain_name, "error": str(e)},
        )

    # CNAME Records
    try:
        answers = dns.resolver.resolve(domain_name, "CNAME")
        result["cname_records"] = [str(rdata) for rdata in answers]
    except Exception as e:
        logger.debug(
            f"No CNAME records para {domain_name}",
            extra={"event": "dns_cname_miss", "domain": domain_name, "error": str(e)},
        )

    return result
