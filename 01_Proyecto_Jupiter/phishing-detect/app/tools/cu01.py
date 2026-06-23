from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import get_logger, session_id_ctx, trace_id_ctx
from app.db.models import DomainAnalysisCache, UserAnalysisHistory
from app.services.phishing_analysis import parse_input, run_phishing_analysis
from app.storage.audit_store import write_audit_event
from app.services.phishing_analysis import _build_llm_explanation

logger = get_logger("tools.cu01")


def _serialize(data: Any) -> Any:
    """
    Convierte datetimes a ISO string para almacenarlas en JSONB

    Args:
        data(Any): Dato a serializar

    Returns:
        Any: Dato con datetimes convertidos a string ISO 8601
    """
    if isinstance(data, dict):
        return {k: _serialize(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_serialize(i) for i in data]
    if isinstance(data, datetime):
        return data.isoformat()
    return data


def _get_cache(domain: str, db: Session) -> DomainAnalysisCache | None:
    """
    Busca una entrada de caché válida sin caducar para el dominio

    Args:
        domain(str): Dominio normalizado
        db(Session): Sesión de base de datos

    Returns:
        DomainAnalysisCache | None: Entrada de caché o None si no existe o caducó
    """
    now = datetime.now(timezone.utc)
    stmt = (
        select(DomainAnalysisCache)
        .where(DomainAnalysisCache.domain_analyzed == domain)
        .where(DomainAnalysisCache.expires_at > now)
        .order_by(DomainAnalysisCache.created_at.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def _save_cache(domain: str, result: dict[str, Any], db: Session) -> DomainAnalysisCache:
    """
    Guarda el resultado del análisis en la caché compartida

    Args:
        domain(str): Dominio analizado
        result(dict[str, Any]): Resultado de run_phishing_analysis
        db(Session): Sesión de base de datos

    Returns:
        DomainAnalysisCache: Entrada de caché creada
    """
    now = datetime.now(timezone.utc)
    entry = DomainAnalysisCache(
        id=uuid.uuid4().hex,
        domain_analyzed=domain,
        risk_score=result["score"],
        risk_level=result["risk_level"],
        target_domain=result.get("target_domain"),
        target_similarity=result.get("target_similarity"),
        indicators_json=result.get("indicators", []),
        whois_json=_serialize(result.get("whois")),
        dns_json=_serialize(result.get("dns")),
        mx_json=_serialize(result.get("mx")),
        virustotal_json=_serialize(result.get("virustotal")),
        created_at=now,
        expires_at=now + timedelta(hours=24),
    )
    db.add(entry)
    db.flush()

    entry._explanation = result.get("explanation", "")

    logger.info(
        f"Caché guardada para {domain}: {entry.risk_level.upper()} ({entry.risk_score}/100)",
        extra={"event": "phishing_cache_saved", "domain": domain},
    )
    return entry


def _save_history(
    user_id: str,
    input_raw: str,
    input_type: str,
    cache_entry: DomainAnalysisCache,
    db: Session,
) -> None:
    """
    Registra la consulta en el historial del usuario

    Args:
        user_id(str): ID del usuario
        input_raw(str): Texto original introducido por el usuario
        input_type(str): Tipo de input: 'url', 'domain' o 'email'
        cache_entry(DomainAnalysisCache): Entrada de caché asociada
        db(Session): Sesión de base de datos
    """
    history = UserAnalysisHistory(
        user_id=user_id,
        input_raw=input_raw[:500],
        input_type=input_type,
        cache_id=cache_entry.id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(history)
    db.flush()


def _cache_to_dict(entry: DomainAnalysisCache, *, from_cache: bool) -> dict[str, Any]:
    """
    Convierte una entrada de caché en el dict de respuesta para el handler

    Args:
        entry(DomainAnalysisCache): Entrada de caché
        from_cache(bool): True si el resultado viene de caché

    Returns:
        dict[str, Any]: Datos del análisis listos para el handler
    """
    explanation = getattr(entry, "_explanation", None)

    return {
        "domain": entry.domain_analyzed,
        "score": entry.risk_score,
        "risk_level": entry.risk_level,
        "indicators": entry.indicators_json or [],
        "target_domain": entry.target_domain,
        "target_similarity": entry.target_similarity,
        "explanation": explanation,
        "from_cache": from_cache,
        "analyzed_at": entry.created_at.isoformat() if entry.created_at else None,
    }


def get_or_run_analysis(
    user_id: str,
    raw_input: str,
    client: OpenAI,
    model: str,
    *,
    db: Session,
) -> dict[str, Any]:
    """
    Devuelve el análisis de phishing, usando caché si está disponible
    Comprueba si existe un análisis reciente (< 24h) para el dominio
    Si no existe, ejecuta el pipeline completo y guarda el resultado
    En ambos casos registra la consulta en el historial del usuario

    Args:
        user_id(str): ID del usuario que realiza la consulta.
        raw_input(str): Texto original del usuario (URL, dominio o email).
        client(OpenAI): Cliente OpenAI para la explicación LLM.
        model(str): Modelo OpenAI a usar.
        db(Session): Sesión de base de datos.

    Returns:
        dict[str, Any]: Resultado del análisis con score, risk_level, explanation, etc.
    """
    domain, input_type = parse_input(raw_input)

    if not domain:
        return {"error": "No se pudo extraer un dominio válido del input.", "domain": None}

    cache_entry = _get_cache(domain, db)
    from_cache = cache_entry is not None

    if not cache_entry:
        result = run_phishing_analysis(domain=domain, client=client, model=model)
        cache_entry = _save_cache(domain, result, db)
        explanation = cache_entry._explanation
    else:
        typosquatting = (
            (cache_entry.target_domain, cache_entry.target_similarity)
            if cache_entry.target_domain
            else None
        )
        explanation = _build_llm_explanation(
            domain=domain,
            score=cache_entry.risk_score,
            risk_level=cache_entry.risk_level,
            indicators=cache_entry.indicators_json or [],
            typosquatting=typosquatting,
            client=client,
            model=model,
        )

    cache_entry._explanation = explanation

    _save_history(
        user_id=user_id,
        input_raw=raw_input,
        input_type=input_type,
        cache_entry=cache_entry,
        db=db,
    )

    write_audit_event(
        trace_id=trace_id_ctx.get(),
        user_id=user_id,
        session_id=session_id_ctx.get(),
        event="domain_phishing_queried",
        payload={
            "domain": domain,
            "input_type": input_type,
            "from_cache": from_cache,
            "risk_level": cache_entry.risk_level,
            "score": cache_entry.risk_score,
        },
    )

    return _cache_to_dict(cache_entry, from_cache=from_cache)
