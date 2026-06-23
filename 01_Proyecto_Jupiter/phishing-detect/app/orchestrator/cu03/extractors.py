from __future__ import annotations

import re
from typing import Any

# Patrones para detectar email, dominios, dias y horas
_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_DOMAIN_RE = re.compile(r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", re.I)
_DAYS_RE = re.compile(r"\b(\d{1,3})\s*d[ií]as?\b", re.I)
_TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")

_LIST_ALERT_PATTERNS = [
    r"\b(mis\s+alertas?|ver\s+alertas?|lista\s+alertas?|mostrar\s+alertas?|alertas\s+activas?|alertas\s+registradas?)\b",  # noqa: E501
    r"\b(qu[eé]\s+alertas?\s+tengo|cu[aá]les\s+son\s+mis\s+alertas?|mis\s+reglas?\s+de\s+alerta)\b",
    r"^\s*alertas?\s*$",
    r"^\s*ver\s*$",
    r"^\s*listar\s*$",
]

_DELETE_ALERT_PATTERN = re.compile(
    r"\b(elimina|eliminar|borra|borrar|quita|quitar|baja|dar\s+de\s+baja)\b[^.]*\b(alerta|regla)\b",
    re.I,
)

_PAUSE_ALERT_PATTERN = re.compile(
    r"\b(pausa|pausar|desactiva|desactivar)\b[^.]*\b(alerta|regla)\b",
    re.I,
)

_ENABLE_ALERT_PATTERN = re.compile(
    r"\b(activar|reanuda|reanudar)\b[^.]*\b(alerta|regla)\b",
    re.I,
)

_ALERT_NAME_STOP_WORDS = {
    "eliminar", "elimina", "borrar", "borra", "quitar", "quita",
    "pausar", "pausa", "desactivar", "desactiva",
    "activar", "activa", "reanudar", "reanuda",
    "la", "el", "los", "las", "del", "de", "mi", "mis",
    "alerta", "alertas", "regla", "reglas",
    "llamada", "llamado", "nombrada", "nombrado",
}

_DELETE_ALERT_STANDALONE = re.compile(
    r"^\s*(elimina|eliminar|borra|borrar|quita|quitar)\s*$", re.I
)

_PAUSE_ALERT_STANDALONE = re.compile(
    r"^\s*(pausa|pausar|desactiva|desactivar)\s*$", re.I
)

_ENABLE_ALERT_STANDALONE = re.compile(
    r"^\s*(activa|activar|reanuda|reanudar)\s*$", re.I
)


def _extract_rule_name(message: str) -> str | None:
    """
    Funcion para extraer el nombre de la Alerta

    Args:
        message (str): Mensaje escrito por el usuario

    Returns:
        str | None: Devuelve el nombre de la regla
    """
    text = (message or "").strip()
    if not text:
        return None

    # Busca cadenas de texto que estan entre comillas simples o comillas dobles.
    # El texto debe tener entre 3 y 80 caracteres.
    quoted_match = re.search(r"'([^']{3,80})'|\"([^\"]{3,80})\"", text)
    if quoted_match:
        return (quoted_match.group(1) or quoted_match.group(2) or "").strip()

    # Si el usuario no ha puesto comillas simples o dobles busca
    # texto con la keyword 'alerta' con variaciones opcionales
    named_match = re.search(
        r"(?:nombre(?:\s+de\s+la\s+alerta)?|alerta)\s*[:=]\s*(.+)$",
        text,
        re.I,
    )
    if named_match:
        candidate = named_match.group(1).strip(" .,:;\"'")
        if 3 <= len(candidate) <= 80:
            return candidate

    return None


def _extract_alert_name(text: str) -> str | None:
    """
    Intenta extraer el nombre de una alerta del mensaje.

    Args:
        text(str): Texto del mensaje en minúsculas

    Returns:
        str | None: Nombre de alerta extraído o None
    """
    # Prioridad 1: cadena entre comillas
    m = re.search(r"['\"]([^'\"]{3,80})['\"]", text)
    if m:
        return m.group(1).strip()

    # Prioridad 2: después de "llamada/nombrada/con nombre X"
    m = re.search(
        r"\b(?:alerta|regla)\b\s+(?:llamad[ao]|nombrad[ao]|con\s+nombre\s+)(.{3,80}?)(?:\s*$|\s*[,;.])",
        text,
        re.I,
    )
    if m:
        candidate = m.group(1).strip(" .,:;\"'")
        if 3 <= len(candidate) <= 80 and candidate.lower() not in _ALERT_NAME_STOP_WORDS:
            return candidate

    # Prioridad 3: lo que viene después de "alerta" o "regla"
    m = re.search(
        r"\b(?:alerta|regla)\b\s+(.{3,80}?)(?:\s*$|\s*[,;.])",
        text,
        re.I,
    )
    if m:
        candidate = m.group(1).strip(" .,:;\"'")
        if 3 <= len(candidate) <= 80 and candidate.lower() not in _ALERT_NAME_STOP_WORDS:
            return candidate

    return None


def regex_extract(message: str) -> dict[str, Any]:
    """
    Función para determinar el parámetro que el usuario ha escrito

    Args:
        message(str): Mensaje escrito por el usuario

    Returns:
        dict[str, Any]: Diccionario con los parámetros detectados
    """
    text = message or ""
    key = text.lower()
    patch: dict[str, Any] = {}

    rule_name = _extract_rule_name(text)
    if rule_name:
        patch["rule_name"] = rule_name

    if "cadu" in key or "expir" in key:
        patch["rule_type"] = "expiry"
        patch["severity"] = "medium"

    msg = _DAYS_RE.search(text)
    if msg:
        patch["condition"] = {"days_before_expiry": int(msg.group(1))}

    em = _EMAIL_RE.search(text)
    if em:
        patch["channels"] = [{"kind": "email", "to": em.group(0)}]

    text_without_emails = _EMAIL_RE.sub(" ", text)
    doms = _DOMAIN_RE.findall(text_without_emails)
    if doms:
        patch["scope"] = {"target_type": "domains", "domains": sorted({d.lower() for d in doms})}

    if "diar" in key or "cada dia" in key or "todos los días" in key or "todos los dias" in key:
        patch["schedule"] = {"frequency": "daily"}
    elif "seman" in key:
        patch["schedule"] = {"frequency": "weekly"}

    tm = _TIME_RE.search(text)
    if tm:
        schedule = patch.get("schedule", {})
        if not isinstance(schedule, dict):
            schedule = {}
        schedule["at_time"] = f"{int(tm.group(1)):02d}:{tm.group(2)}"
        patch["schedule"] = schedule

    if ("riesgo alto" in key or "alto riesgo" in key) and "condition" not in patch:
        patch["condition"] = {"risk_level": "high"}

    if "no quiero cooldown" in key or "sin cooldown" in key:
        patch["cooldown"] = {"seconds": 0}

    return patch


def extract_cu03_crud_intent(message: str) -> dict[str, Any]:
    """
    Detecta la intención CRUD sobre alertas en el mensaje del usuario

    Args:
        message(str): Mensaje del usuario

    Returns:
        dict: {"intent": "list"|"delete"|"pause"|"enable"|None,
               "rule_name": str|None}
    """
    text = " ".join(message.strip().lower().split())

    for pattern in _LIST_ALERT_PATTERNS:
        if re.search(pattern, text, re.I):
            return {"intent": "list", "rule_name": None}

    if _DELETE_ALERT_PATTERN.search(text) or _DELETE_ALERT_STANDALONE.search(text):
        return {"intent": "delete", "rule_name": _extract_alert_name(text)}

    if _PAUSE_ALERT_PATTERN.search(text) or _PAUSE_ALERT_STANDALONE.search(text):
        return {"intent": "pause", "rule_name": _extract_alert_name(text)}

    if _ENABLE_ALERT_PATTERN.search(text) or _ENABLE_ALERT_STANDALONE.search(text):
        return {"intent": "enable", "rule_name": _extract_alert_name(text)}

    return {"intent": None, "rule_name": None}
