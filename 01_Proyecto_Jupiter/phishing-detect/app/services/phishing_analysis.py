from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jellyfish
import tldextract
from openai import OpenAI

from app.core.logging import get_logger, log_event
from app.data.tranco_loader import load_tranco_domains
from app.services.domain_analysis import analyze_domain
from app.services.reputation import check_domain_reputation
from app.integrations.reputation.virustotal import VirusTotalProvider


logger = get_logger("services.phishing_analysis")

_LEGITIMATE_DOMAINS_FILE = Path(__file__).parent.parent / "data" / "legitimate_domains.json"
_GENERIC_SLDS = {"gob", "gov", "com", "net", "org", "edu"}
_SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "xyz", "top", "club",
    "work", "party", "gdn", "win", "bid", "download", "racing",
}
_PART_STOPWORDS = {
    "login", "secure", "seguro", "mail", "www", "web", "account", "cuenta",
    "signin", "sign", "auth", "portal", "update", "verify", "support",
    "help", "service", "online", "client", "info", "access", "acceso",
    "bank", "banca", "pay", "pago", "shop", "store", "tienda", "alert",
    "confirm", "reset", "recover", "verificar", "official", "ofcial",
}

# Se usa solo una vez mientras el proceso siga vivo (caché)
_brand_index: list[tuple[str, str]] | None = None


def _extract_brand(domain: str) -> str:
    """
    Extrae el nombre de marca de un dominio.

    Para dominios tipo 'agenciatributaria.gob.es' devuelve 'agenciatributaria'
    en lugar de 'gob'.

    Args:
        domain(str): Dominio completo

    Returns:
        str: Nombre de marca en minúsculas
    """
    ext = tldextract.extract(domain)
    if ext.domain.lower() in _GENERIC_SLDS and ext.subdomain:
        return ext.subdomain.split(".")[-1].lower()
    return ext.domain.lower()


def _load_brand_index() -> list[tuple[str, str]]:
    """
    Carga el índice de marcas legítimas (Tranco + lista curada española)

    Returns:
        list[tuple[str, str]]: Lista de (brand, full_domain)
    """
    global _brand_index
    if _brand_index is not None:
        return _brand_index

    domains: list[str] = []

    domains.extend(load_tranco_domains())

    try:
        data = json.loads(_LEGITIMATE_DOMAINS_FILE.read_text(encoding="utf-8"))
        domains.extend(data.get("domains", []))
    except Exception as e:
        log_event(
            logger,
            level=40,
            event="brand_index_load_error",
            message="Error cargando lista curada",
            extra={"error": str(e)},
            exc_info=True,
        )

    index: list[tuple[str, str]] = []
    seen: set[str] = set()
    for domain in domains:
        brand = _extract_brand(domain)
        if brand and brand not in seen:
            seen.add(brand)
            index.append((brand, domain))

    _brand_index = index
    log_event(
        logger,
        level=20,
        event="brand_index_loaded",
        message="Índice de marcas cargado",
        extra={"count": len(index)},
    )
    return _brand_index


def _find_typosquatting_target(domain: str) -> tuple[str, float] | None:
    """
    Busca el dominio legítimo más similar usando tres estrategias

    1. Combosquatting: marca conocida contenida en el brand analizado
    2. Partes de dominio: analiza cada parte del brand separada por guiones
    3. Jaro-Winkler: similitud global con pre-filtrado por longitud

    Args:
        domain(str): Dominio analizado.

    Returns:
        tuple[str, float] | None: (dominio_objetivo, similitud) o None si no hay match.
    """
    brand = _extract_brand(domain)
    if not brand:
        return None

    brand_index = _load_brand_index()

    # Ejemplo Combosquatting: "login-paypal" contiene "paypal" suplantación de paypal.com
    for legit_brand, legit_domain in brand_index:
        if len(legit_brand) >= 4 and legit_brand in brand and brand != legit_brand:
            return legit_domain, 0.95

    # Análisis por partes (dominios con guión)
    # Ejemplo: "login-paypa1" → partes ["login", "paypa1"]
    parts = [p for p in brand.split("-") if len(p) >= 4 and p not in _PART_STOPWORDS]
    if parts and "-" in brand:
        best_part_domain: str | None = None
        best_part_score = 0.0
        for part in parts:
            for legit_brand, legit_domain in brand_index:
                if part == legit_brand:
                    return legit_domain, 1.0  # coincidencia exacta en una parte
                score = jellyfish.jaro_winkler_similarity(part, legit_brand)
                if score > best_part_score:
                    best_part_score = score
                    best_part_domain = legit_domain
        if best_part_score >= 0.85 and best_part_domain:
            return best_part_domain, round(best_part_score, 4)

    # Jaro-Winkler sobre el brand completo con pre-filtrado por longitud
    brand_len = len(brand)
    candidates = [
        (b, d) for b, d in brand_index
        if abs(len(b) - brand_len) <= 3
    ]

    best_domain: str | None = None
    best_score = 0.0

    for legit_brand, legit_domain in candidates:
        if brand == legit_brand:
            return None  # Es el dominio legítimo

        score = jellyfish.jaro_winkler_similarity(brand, legit_brand)
        if score > best_score:
            best_score = score
            best_domain = legit_domain

    if best_score >= 0.70 and best_domain:
        return best_domain, round(best_score, 4)

    return None


def _calculate_score(
    domain: str,
    whois_data: dict[str, Any],
    reputation_data: dict[str, Any],
    typosquatting: tuple[str, float] | None,
) -> tuple[int, str, list[str]]:
    """
    Calcula el score de riesgo de phishing (0-100) de forma determinística

    Args:
        domain(str): Dominio analizado
        whois_data(dict[str, Any]): Datos WHOIS del dominio
        reputation_data(dict[str, Any]): Datos de reputación (VirusTotal)
        typosquatting(tuple[str, float] | None): Resultado del análisis de typosquatting

    Returns:
        tuple[int, str, list[str]]: (score, risk_level, indicadores)
    """
    score = 0
    indicators: list[str] = []
    ext = tldextract.extract(domain)

    # VirusTotal (0-40 pts)
    vt_data = reputation_data.get("providers", {}).get("virustotal", {})
    malicious = vt_data.get("malicious") or 0
    suspicious = vt_data.get("suspicious") or 0

    vt_score = VirusTotalProvider.malicious_to_score(malicious, suspicious)
    vt_contribution = round(vt_score * 0.4)
    if vt_contribution > 0:
        score += vt_contribution
        if malicious:
            indicators.append(f"{malicious} motores de VirusTotal lo marcan como malicioso")
        elif suspicious:
            indicators.append(f"{suspicious} motores de VirusTotal lo marcan como sospechoso")

    # Edad del dominio (0-25 pts)
    creation_date = whois_data.get("creation_date")
    if isinstance(creation_date, datetime):
        if creation_date.tzinfo is None:
            creation_date = creation_date.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - creation_date).days
        if age_days < 7:
            score += 25
            indicators.append(f"Dominio registrado hace solo {age_days} días")
        elif age_days < 30:
            score += 20
            indicators.append(f"Dominio muy reciente ({age_days} días)")
        elif age_days < 90:
            score += 10
            indicators.append(f"Dominio reciente ({age_days} días)")
        elif age_days < 365:
            score += 5

    # Typosquatting (0-20 pts)
    if typosquatting:
        target_domain, similarity = typosquatting
        pct = round(similarity * 100)
        if similarity >= 0.90:
            score += 20
        elif similarity >= 0.80:
            score += 15
        else:
            score += 10
        indicators.append(f"Similitud del {pct}% con {target_domain} (posible suplantación)")

    # Estructura (0-10 pts)
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain):
        score += 10
        indicators.append("URL contiene dirección IP en lugar de nombre de dominio")
    elif ext.subdomain:
        subdomain_parts = ext.subdomain.split(".")
        if len(subdomain_parts) > 2:
            score += 5
            indicators.append(f"Exceso de subdominios ({len(subdomain_parts)})")

    # TLD sospechoso (0-5 pts)
    tld = ext.suffix.split(".")[-1] if ext.suffix else ""
    if tld in _SUSPICIOUS_TLDS:
        score += 5
        indicators.append(f"TLD sospechoso (.{tld})")

    score = min(score, 100)

    if score >= 81:
        risk_level = "critico"
    elif score >= 61:
        risk_level = "alto"
    elif score >= 31:
        risk_level = "medio"
    else:
        risk_level = "bajo"

    return score, risk_level, indicators


def _build_llm_explanation(
    domain: str,
    score: int,
    risk_level: str,
    indicators: list[str],
    typosquatting: tuple[str, float] | None,
    client: OpenAI,
    model: str,
) -> str:
    """
    Genera explicación en lenguaje natural usando LLM

    Args:
        domain(str): Dominio analizado
        score(int): Score de riesgo (0-100)
        risk_level(str): Nivel de riesgo (bajo/medio/alto/critico)
        indicators(list[str]): Lista de indicadores detectados
        typosquatting(tuple[str, float] | None): Dominio objetivo y similitud
        client(OpenAI): Cliente OpenAI
        model(str): Modelo a usar

    Returns:
        str: Explicación en español generada por el LLM.
    """
    target_info = ""
    if typosquatting:
        target_info = (
            f"\nDominio legítimo suplantado: {typosquatting[0]} "
            f"(similitud {round(typosquatting[1] * 100)}%)"
        )

    indicators_text = (
        "\n".join(f"- {i}" for i in indicators)
        if indicators
        else "- Sin indicadores de riesgo detectados"
    )

    system_prompt = (
        "Eres un experto en ciberseguridad especializado en detección de phishing. "
        "Explica de forma clara y concisa en español si un dominio es sospechoso de phishing y por qué. "
        "Usa un tono profesional pero comprensible. Máximo 4 frases."
    )

    user_prompt = (
        f"Dominio analizado: {domain}\n"
        f"Score de riesgo: {score}/100\n"
        f"Nivel de riesgo: {risk_level.upper()}\n"
        f"Indicadores detectados:\n{indicators_text}"
        f"{target_info}\n\n"
        "Genera una explicación en español del análisis."
    )

    log_event(
        logger,
        level=20,
        event="phishing_llm_start",
        message="Generando explicación LLM",
        extra={"domain": domain, "score": score, "risk_level": risk_level},
    )

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        log_event(
            logger,
            level=40,
            event="phishing_llm_error",
            message="Error generando explicación LLM",
            extra={"error": str(e)},
            exc_info=True,
        )
        return f"Análisis completado. Nivel de riesgo: {risk_level.upper()} ({score}/100)."


def parse_input(raw_input: str) -> tuple[str, str]:
    """
    Extrae el dominio y tipo de entrada desde texto libre del usuario

    Args:
        raw_input(str): Texto del usuario (URL, dominio o email)

    Returns:
        tuple[str, str]: (dominio_extraído, input_type). input_type puede ser url, dominio o email
    """
    raw = raw_input.strip().lower()

    if "@" in raw and not raw.startswith("http"):
        domain_part = raw.split("@")[-1]
        ext = tldextract.extract(domain_part)
        if ext.domain and ext.suffix:
            return f"{ext.domain}.{ext.suffix}", "email"
        return domain_part, "email"

    ext = tldextract.extract(raw)
    input_type = "url" if raw.startswith("http") or "/" in raw else "domain"

    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}", input_type

    return raw, input_type


def run_phishing_analysis(
    domain: str,
    client: OpenAI,
    model: str,
) -> dict[str, Any]:
    """Ejecuta el pipeline completo de análisis de phishing

    Args:
        domain(str): Dominio extraído del input del usuario
        client(OpenAI): Cliente OpenAI para la explicación LLM
        model(str): Modelo OpenAI a usar

    Returns:
        dict[str, Any]: Resultado con score, risk_level, indicators, target, explanation y datos crudos.
    """
    log_event(
        logger,
        level=20,
        event="phishing_analysis_start",
        message="Iniciando análisis de phishing",
        extra={"domain": domain},
    )

    analysis = analyze_domain(domain)
    whois_data = analysis.get("whois", {})
    dns_data = analysis.get("dns", {})
    mx_data = analysis.get("mx", {})

    reputation_data = check_domain_reputation(domain)

    typosquatting = _find_typosquatting_target(domain)

    score, risk_level, indicators = _calculate_score(
        domain=domain,
        whois_data=whois_data,
        reputation_data=reputation_data,
        typosquatting=typosquatting,
    )

    explanation = _build_llm_explanation(
        domain=domain,
        score=score,
        risk_level=risk_level,
        indicators=indicators,
        typosquatting=typosquatting,
        client=client,
        model=model,
    )

    log_event(
        logger,
        level=20,
        event="phishing_analysis_done",
        message="Análisis de phishing completado",
        extra={"domain": domain, "score": score, "risk_level": risk_level},
    )

    return {
        "domain": domain,
        "score": score,
        "risk_level": risk_level,
        "indicators": indicators,
        "target_domain": typosquatting[0] if typosquatting else None,
        "target_similarity": typosquatting[1] if typosquatting else None,
        "explanation": explanation,
        "whois": whois_data,
        "dns": dns_data,
        "mx": mx_data,
        "virustotal": reputation_data.get("providers", {}).get("virustotal", {}),
    }
