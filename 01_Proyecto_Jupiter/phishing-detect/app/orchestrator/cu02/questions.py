from __future__ import annotations

from typing import Any

_CANCEL_HINT = 'Puedes escribir "cancelar" para salir.'


def with_cancel_hint(text: str) -> str:
    """ Añade a la respuesta el mensaje de poder cancelar para salir """
    return f"{text}\n\n{_CANCEL_HINT}"


def build_question_for_missing(draft: dict[str, Any], missing: list[str]) -> str:
    """
    Genera la pregunta al usuario para el primer campo pendiente

    Args:
        draft(dict[str, Any]): Borrador actual
        missing(list[str]): Campos pendientes

    Returns:
        str: Pregunta al usuario
    """
    m = missing[0]

    if m == "domain_name":
        return with_cancel_hint("¿Qué dominio quieres registrar? (ej: ejemplo.com)")

    return with_cancel_hint("Necesito más datos. ¿Puedes indicarme el dominio?")


def build_tags_question(domain_name: str) -> str:
    """ Pregunta por etiquetas opcionales tras confirmar el dominio """
    return with_cancel_hint(
        f"Dominio **{domain_name}** listo. "
        "¿Quieres añadir etiquetas? (ej: tags: marca, cliente) "
        "o escribe **no** para ninguna."
    )
