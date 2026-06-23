from __future__ import annotations

import json
from dataclasses import dataclass
from openai import OpenAI

from app.core.logging import get_logger

logger = get_logger("router")

OPTION_LOOKUP_DOMAIN = "OPTION_01_LOOKUP_DOMAIN"
OPTION_CREATE_DOMAIN = "OPTION_02_CREATE_DOMAIN"
OPTION_CREATE_ALERT = "OPTION_03_CREATE_ALERT"
OPTION_RAG_QUERY = "OPTION_04_RAG_QUERY"
OPTION_UNKNOWN = "OPTION_UNKNOWN"

MENU_OPTIONS = {
    OPTION_LOOKUP_DOMAIN: "01.- Analizar phishing de un dominio o URL",
    OPTION_CREATE_DOMAIN: "02.- Gestión de dominios",
    OPTION_CREATE_ALERT: "03.- Gestión de Alertas",
    OPTION_RAG_QUERY: "04.- Consultar base de conocimiento",
}

REGISTER_PREFIXES = (
    "registrar ", "dar de alta ", "añadir dominio ", "alta dominio ",
    "mis dominios", "ver dominios", "ver mis dominios", "lista dominios", "mostrar dominios",
    "elimina ", "eliminar ", "borra ", "borrar ", "desactiva ", "activa ",
    "cambia tags ", "cambia etiquetas ", "actualiza tags ",
)
ANALYZE_PREFIXES = ("analizar ", "analiza ", "comprobar ", "verificar ", "es phishing ")


@dataclass
class RouteDecision:
    option: str
    confidence: float
    reason: str


def build_menu_message(prefix: str) -> str:
    return f"{prefix}"


def route_message(text: str, model: str, client: OpenAI) -> RouteDecision:
    normalized = " ".join((text or "").strip().lower().split())

    exact_match_map = {
        # Para analizar en busca de phishing
        "analizar phishing de un dominio o url": OPTION_LOOKUP_DOMAIN,
        "analizar phishing": OPTION_LOOKUP_DOMAIN,
        "analizar dominio": OPTION_LOOKUP_DOMAIN,
        "es phishing": OPTION_LOOKUP_DOMAIN,
        "01": OPTION_LOOKUP_DOMAIN,
        "1": OPTION_LOOKUP_DOMAIN,

        # Para dar de alta un dominio
        "gestionar los dominios": OPTION_CREATE_DOMAIN,
        "02": OPTION_CREATE_DOMAIN,
        "2": OPTION_CREATE_DOMAIN,

        # Para alertas
        "gestionar las alertas": OPTION_CREATE_ALERT,
        "03": OPTION_CREATE_ALERT,
        "3": OPTION_CREATE_ALERT,

        # Para consultar la base de conocimiento RAG
        "consultar base de conocimiento": OPTION_RAG_QUERY,
        "base de conocimiento": OPTION_RAG_QUERY,
        "consultar conocimiento": OPTION_RAG_QUERY,
        "04": OPTION_RAG_QUERY,
        "4": OPTION_RAG_QUERY,
    }

    exact_match = exact_match_map.get(normalized)
    if exact_match:
        return RouteDecision(
            option=exact_match,
            confidence=1.0,
            reason="exact_menu_match",
        )

    for kw in REGISTER_PREFIXES:
        if normalized.startswith(kw):
            return RouteDecision(
                option=OPTION_CREATE_DOMAIN,
                confidence=1.0,
                reason="keyword_prefix_match",
            )

    for kw in ANALYZE_PREFIXES:
        if normalized.startswith(kw):
            return RouteDecision(
                option=OPTION_LOOKUP_DOMAIN,
                confidence=1.0,
                reason="keyword_prefix_match",
            )

    prompt = (
        "Clasifica la intencion del usuario en una opcion del menu.\n"
        "Responde solo JSON valido con las claves option, confidence y reason.\n"
        f"Opciones validas: {', '.join(MENU_OPTIONS.keys())}, {OPTION_UNKNOWN}.\n"
        "Usa OPTION_UNKNOWN si el mensaje no corresponde claramente a una opcion del menu."
    )

    logger.info(
        "Llamada LLM para clasificación de menú",
        extra={"event": "router_llm_start", "text": text[:100]},
    )

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text or ""},
            ],
        )
        payload = json.loads(response.choices[0].message.content or "{}")

    except Exception as e:
        logger.warning(
            f"Error en el router LLM: {e}",
            extra={"event": "router_llm_error", "error": str(e)},
        )
        return RouteDecision(
            option=OPTION_UNKNOWN,
            confidence=0.0,
            reason="router_llm_error",
        )

    option = payload.get("option")
    if option not in MENU_OPTIONS and option != OPTION_UNKNOWN:
        option = OPTION_UNKNOWN

    try:
        confidence = float(payload.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0

    reason = str(payload.get("reason") or "llm_menu_classification")
    return RouteDecision(option=option or OPTION_UNKNOWN, confidence=confidence, reason=reason)
