from __future__ import annotations

_CANCEL_HINT = 'Puedes escribir "cancelar" para volver al menú.'


def with_cancel_hint(text: str) -> str:
    """Añade al mensaje el hint de cancelación."""
    return f"{text}\n\n{_CANCEL_HINT}"


def ask_for_input() -> str:
    """
    Pregunta al usuario el dominio, URL o email a analizar
    """
    return with_cancel_hint(
        "¿Qué dominio, URL o email quieres analizar?\n"
        "(Ejemplos: `paypa1.com`, `https://login-paypal.com/secure`, `soporte@paypa1.com`)"
    )
