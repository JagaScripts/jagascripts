from __future__ import annotations

import re
from typing import Any

_DOMAIN_RE = re.compile(
    r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", re.I
)

_LIST_PATTERNS = [
    r"\b(mis\s+dominios|ver\s+dominios?|lista\s+dominios?|mostrar\s+dominios?|dominios\s+registrados?)\b",
    r"\b(qu[eé]\s+dominios?\s+tengo|cu[aá]les\s+son\s+mis\s+dominios?)\b",
    r"^\s*ver\s*$",
]

_DELETE_PATTERNS = [
    r"\b(elimina|eliminar|borra|borrar|quita|quitar|baja|dar\s+de\s+baja)\b.{0,30}\b(dominio\b.{0,20})?(?P<domain>[a-z0-9][\w\-]{1,61}[a-z0-9]?\.[a-z]{2,})",  # noqa: E501
    r"^(elimina|eliminar|borra|borrar|quita|quitar)$",
]

_UPDATE_STATUS_PATTERNS = [
    r"\b(?P<action>desactiva|desactivar|activa(?!r)|activar|pausa|pausar)\b.{0,30}\b(?P<domain>[a-z0-9][\w\-]{1,61}[a-z0-9]?\.[a-z]{2,})",  # noqa: E501
    r"\b(?P<domain>[a-z0-9][\w\-]{1,61}[a-z0-9]?\.[a-z]{2,})\b.{0,20}\b(?P<action>desactiva|desactivar|activa|activar|pausa|pausar)\b",  # noqa: E501
]

_UPDATE_TAGS_PATTERNS = [
    r"\b(cambia|cambiar|actualiza|actualizar|modifica|modificar)\b.{0,20}\b(tags?|etiquetas?)\b.{0,30}\b(?P<domain>[a-z0-9][\w\-]{1,61}[a-z0-9]?\.[a-z]{2,})",  # noqa: E501
    r"\b(?P<domain>[a-z0-9][\w\-]{1,61}[a-z0-9]?\.[a-z]{2,})\b.{0,20}\b(tags?|etiquetas?)\b",
    r"^\s*(actualizar|actualiza|modificar|modifica)\s*$",
]

_NO_TAGS_KEYWORDS = {"no", "ninguna", "ninguno", "sin", "nada", "skip", "omitir"}


def regex_extract(message: str) -> dict[str, Any]:
    """
    Extrae domain_name y tags del mensaje del usuario

    Args:
        message(str): Mensaje del usuario

    Returns:
        dict[str, Any]: Campos detectados (domain_name, tags)
    """
    text = message or ""
    patch: dict[str, Any] = {}

    domains = _DOMAIN_RE.findall(text)
    if domains:
        patch["domain_name"] = domains[0].lower()

    key = text.strip().lower()

    # Tags explícitas: "tags: marca, cliente" o "etiquetas: marca"
    tag_match = re.search(r"(?:tags?|etiquetas?)\s*[:=]\s*(.+)", text, re.I)
    if tag_match:
        raw_tags = tag_match.group(1)
        tags = [t.strip().lower() for t in re.split(r"[,;]", raw_tags) if t.strip()]
        patch["tags"] = tags[:10]
    elif key in _NO_TAGS_KEYWORDS or key.startswith("no ") or "sin etiqueta" in key:
        patch["tags"] = []

    return patch


def extract_crud_intent(message: str) -> dict[str, Any]:
    """
    Detecta la intención CRUD en el mensaje del usuario

    Args:
        message(str): Mensaje del usuario

    Returns:
        dict: {"intent": "list"|"delete"|"update_status"|"update_tags"|None,
               "domain_name": str|None,
               "new_status": "active"|"inactive"|None,
               "new_tags": list[str]|None}
    """
    text = " ".join(message.strip().lower().split())

    # Listar
    for pattern in _LIST_PATTERNS:
        if re.search(pattern, text):
            return {"intent": "list", "domain_name": None, "new_status": None, "new_tags": None}

    # Eliminar
    for pattern in _DELETE_PATTERNS:
        m = re.search(pattern, text)
        if m:
            return {
                "intent": "delete",
                "domain_name": m.groupdict().get("domain"),
                "new_status": None,
                "new_tags": None,
            }

    # Actualizar estado
    for pattern in _UPDATE_STATUS_PATTERNS:
        m = re.search(pattern, text)
        if m:
            action = m.group("action")
            new_status = "inactivo" if any(w in action for w in ("desactiv", "paus")) else "activo"
            return {
                "intent": "update_status",
                "domain_name": m.group("domain"),
                "new_status": new_status,
                "new_tags": None,
            }

    # actualizar tags
    for pattern in _UPDATE_TAGS_PATTERNS:
        m = re.search(pattern, text)
        if m:
            return {
                "intent": "update_tags",
                "domain_name": m.groupdict().get("domain"),
                "new_status": None,
                "new_tags": None,
            }

    return {"intent": None, "domain_name": None, "new_status": None, "new_tags": None}
