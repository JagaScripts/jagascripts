from __future__ import annotations

import re

_MENU_ONLY = re.compile(
    r"^\s*(?:04|4|consultar\s+base(?:\s+de\s+conocimiento)?|base\s+de\s+conocimiento|rag|conocimiento)\s*$",
    flags=re.IGNORECASE,
)

_QUESTION_PREFIXES = re.compile(
    r"^\s*(?:consultar?|pregunta[r]?|quiero\s+saber|dime|expl[ií]ca(?:me)?)\s*[:\-,]?\s*",
    flags=re.IGNORECASE,
)


def extract_question(message: str) -> str | None:
    """
    Extrae la pregunta RAG del mensaje del usuario

    Si el mensaje es solo la selección de menú (ej: "04", "4"), devuelve None
    En caso contrario, limpia prefijos conversacionales y devuelve la pregunta

    Args:
        message(str): Mensaje del usuario

    Returns:
        str | None: Pregunta limpia, o None si el mensaje es solo selección de opción
    """
    text = (message or "").strip()

    if _MENU_ONLY.match(text):
        return None

    cleaned = _QUESTION_PREFIXES.sub("", text).strip()
    return cleaned if cleaned else None
