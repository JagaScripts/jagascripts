from __future__ import annotations

import re
from typing import Any

_URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.I)
_DOMAIN_RE = re.compile(
    r"\b(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}\b", re.I
)


def regex_extract(message: str) -> dict[str, Any]:
    """
    Extrae URL, dominio o email del mensaje del usuario en ese orden

    Args:
        message(str): Mensaje del usuario

    Returns:
        dict[str, Any]: {'raw_input': str} si se detecta algo, o {} si no
    """
    text = message or ""

    url_match = _URL_RE.search(text)
    if url_match:
        return {"raw_input": url_match.group(0)}

    email_match = _EMAIL_RE.search(text)
    if email_match:
        return {"raw_input": email_match.group(0)}

    domain_match = _DOMAIN_RE.search(text)
    if domain_match:
        return {"raw_input": domain_match.group(0)}

    return {}
