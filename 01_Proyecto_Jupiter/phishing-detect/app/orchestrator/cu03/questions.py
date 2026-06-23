from __future__ import annotations

from typing import Any

_CANCEL_HINT = 'Puedes escribir "cancelar" para salir.'


def with_cancel_hint(text: str) -> str:
    """ Añade a la respuesta el mensaje de poder cancelar para salir"""
    return f"{text}\n\n{_CANCEL_HINT}"


def build_question_for_missing(draft: dict[str, Any], missing: list[str]) -> str:
    """
    Crea preguntas al usuario cuando faltan datos para crear la alerta

    Args:
        draft(dict[str, Any]): Borrador del estado de la alerta
        missing(list[str]): Valores faltantes para crear la alerta

    Returns:
        str: Petición al usuario del parámetro que falta
    """

    m = missing[0]

    rule_type = draft.get("rule_type")
    scope = draft.get("scope") or {}
    channels = draft.get("channels") or []
    schedule = draft.get("schedule") or {}

    domains = scope.get("domains") or []
    email = None
    if channels and isinstance(channels, list):
        for ch in channels:
            if isinstance(ch, dict) and ch.get("kind") == "email" and ch.get("to"):
                email = ch["to"]
                break

    if m == "rule_name":
        return with_cancel_hint(
            "Hace falta un nombre para la alerta. Pon el nombre de la alerta entre comillas simples. Ej: 'Alerta Dominio'"  # noqa: E501
        )

    # if m == "rule_type":
    #     return with_cancel_hint("¿La alerta es por **caducidad** del dominio o por **riesgo**?")

    if m == "condition":
        if rule_type == "expiry":
            dom_txt = f" para **{domains[0]}**" if domains else ""
            return with_cancel_hint(
                f"¿Cuántos días antes de la caducidad quieres el aviso{dom_txt}? (ej: 15 días)"
            )
        # if rule_type == "risk":
        #     return with_cancel_hint(
        #         "¿Qué condición de riesgo quieres? (ej: 'riesgo alto' o 'score >= 80')"
        #     )
        return with_cancel_hint(
            "¿Cuál es la condición exacta? (ej: '15 días antes de caducar')"
        )

    if m == "channels":
        if email:
            return with_cancel_hint(
                f"Ya tengo el email **{email}**. ¿Quieres añadir otro canal o confirmo ese?"
            )
        return with_cancel_hint("¿A qué email debo notificarte? (ej: soc@dominio.com)")

    if m == "scope":
        if domains:
            return with_cancel_hint(
                f"Ya tengo el dominio **{domains[0]}**. ¿Aplica solo a ese o a más dominios?"
            )
        return with_cancel_hint("¿Aplica a todos tus dominios o a alguno concreto? (ej: acme.es)")

    if m == "schedule":
        freq = schedule.get("frequency") or schedule.get("frecuency")
        if freq:
            return with_cancel_hint(
                f"Ya tengo frecuencia **{freq}**. ¿A qué hora quieres el aviso? (ej: 09:00)"
            )
        return with_cancel_hint("¿Con qué frecuencia quieres el aviso? (diaria/semanal)")

    return with_cancel_hint("Necesito datos para crear la alerta. ¿Puedes indicármelo? (ejem. 'Avisame cuando un dominio vaya a caducar en 20 días')")  # noqa: E501
