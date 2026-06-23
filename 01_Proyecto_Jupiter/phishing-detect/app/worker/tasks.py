from __future__ import annotations

import os
from datetime import datetime, timezone

from app.db.models import DomainEnrichment
from app.db.session import SessionLocal
from app.services.domain_analysis import analyze_domain
from app.services.reputation import check_domain_reputation
from app.worker.celery_app import celery_app
from app.core.logging import setup_logging, log_event, get_logger
from celery.signals import after_setup_logger


logger = get_logger("worker.enrich_domain")


@after_setup_logger.connect
def init_worker_logging(logger, **kwargs):
    setup_logging(log_file=os.getenv("LOG_FILE", ""))


@celery_app.task(
    bind=True,
    name="app.worker.tasks.enrich_domain",
    max_retries=3,
    default_retry_delay=60,
)
def enrich_domain(self, domain_id: str, domain_name: str) -> dict:
    """
    Enriquece un dominio con WHOIS, DNS, MX y VirusTotal

    Args:
        domain_id(str): ID del dominio a enriquecer
        domain_name(str): Nombre del dominio

    Returns:
        dict[str, Any]: Resultado con enrichment_status y domain_id
    """
    db = SessionLocal()
    try:
        enrichment = db.query(DomainEnrichment).filter_by(domain_id=domain_id).first()
        if not enrichment:
            log_event(
                logger,
                level=40,
                event="enrich_not_found",
                message="Enrichment no encontrado",
                extra={"domain_id": domain_id},
            )
            return {"enrichment_status": "error", "domain_id": domain_id}

        enrichment.enrichment_status = "processing"
        db.commit()

        log_event(
            logger,
            level=20,
            event="enrich_start",
            message="Iniciando enriquecimiento",
            extra={"domain": domain_name, "domain_id": domain_id},
        )

        analysis_data = analyze_domain(domain_name)
        reputation_data = check_domain_reputation(domain_name)

        whois_data = analysis_data.get("whois", {})
        dns_data = analysis_data.get("dns", {})
        mx_data = analysis_data.get("mx", [])
        vt_data = reputation_data.get("providers", {}).get("virustotal", {})
        final_risk_score = reputation_data.get("max_risk_score", 0.0)

        enrichment.whois_registrar = whois_data.get("registrar")
        enrichment.whois_expiration_date = whois_data.get("expiration_date")
        enrichment.whois_creation_date = whois_data.get("creation_date")
        enrichment.whois_registrant = whois_data.get("registrant")
        enrichment.dns_a_records = dns_data.get("a_records")
        enrichment.dns_ns_records = dns_data.get("ns_records")
        enrichment.dns_cname_records = dns_data.get("cname_records")
        enrichment.mx_servers = mx_data
        enrichment.virustotal_malicioso = vt_data.get("malicious")
        enrichment.virustotal_sospechoso = vt_data.get("suspicious")
        enrichment.virustotal_ultima_comprobacion = vt_data.get("last_check_at")
        enrichment.reputation_score = final_risk_score
        enrichment.last_enriched_at = datetime.now(timezone.utc)
        enrichment.last_enrichment_error = analysis_data.get("error")
        enrichment.enrichment_status = "done" if analysis_data.get("error") is None else "error"
        db.commit()

        log_event(
            logger,
            level=20,
            event="enrich_done",
            message="Enriquecimiento completado",
            extra={
                "domain": domain_name,
                "domain_id": domain_id,
                "risk_score": final_risk_score,
                "enrichment_status": enrichment.enrichment_status,
            },
        )
        return {"enrichment_status": enrichment.enrichment_status, "domain_id": domain_id}

    except Exception as e:
        if db:
            try:
                enrichment = db.query(DomainEnrichment).filter_by(domain_id=domain_id).first()
                if enrichment:
                    enrichment.enrichment_status = "error"
                    enrichment.last_enrichment_error = str(e)
                    db.commit()
            except Exception:
                db.rollback()

        log_event(
            logger,
            level=40,
            event="enrich_error",
            message="Error en enriquecimiento",
            extra={"domain": domain_name, "domain_id": domain_id},
            exc_info=True,
        )
        raise self.retry(exc=e)
    finally:
        db.close()
