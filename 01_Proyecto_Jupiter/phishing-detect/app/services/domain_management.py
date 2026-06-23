from __future__ import annotations

import uuid
from typing import Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.logging import get_logger, trace_id_ctx, session_id_ctx, log_event
from app.db.models import Domain, DomainEnrichment
from app.storage.audit_store import write_audit_event
from app.worker.tasks import enrich_domain

logger = get_logger("domain_management_service")


def create_domain(
    user_id: str,
    domain_name: str,
    tags: list[str] | None = None,
    status: str = "activo",
    *,
    db: Session,
) -> dict[str, Any]:
    """
    Crea un dominio y lo enriquece con datos de WHOIS, DNS, MX y reputación

    Args:
        user_id(str): ID del usuario propietario
        domain_name(str): Nombre del dominio
        tags(list[str] | None): Etiquetas opcionales
        status(str): "activo" o "inactivo"
        db(Session): Sesión de BD

    Returns:
        dict[str, Any]: Datos del dominio creado
    """
    try:
        log_event(
            logger,
            level=20,
            event="domain_create_start",
            message="Creando dominio",
            extra={"domain": domain_name, "user_id": user_id},
        )

        domain_id = f"dom_{uuid.uuid4().hex[:12]}"
        enrichment_id = f"en_{uuid.uuid4().hex[:12]}"

        domain = Domain(
            id=domain_id,
            user_id=user_id,
            domain_name=domain_name,
            status=status,
            tags=tags or [],
        )
        db.add(domain)
        db.flush()  # Asegurar que se persista antes de crear enrichment

        enrichment = DomainEnrichment(
            id=enrichment_id,
            domain_id=domain_id,
            enrichment_status="pending",
            reputation_score=0.0,
            last_enriched_at=datetime.now(timezone.utc),
        )
        db.add(enrichment)
        db.commit()

        enrich_domain.delay(domain_id, domain_name)

        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id,
            session_id=session_id_ctx.get(),
            event="domain_registered",
            payload={
                "domain_id": domain_id,
                "domain_name": domain_name,
                "status": status,
                "tags": tags or [],
                "reputation_score": 0.0,
                "enrichment_status": "pending",
            },
        )

        log_event(
            logger,
            level=20,
            event="domain_create_complete",
            message="Dominio creado",
            extra={"domain_id": domain_id, "domain": domain_name},
        )

        return {
            "domain_id": domain_id,
            "domain_name": domain_name,
            "created": True,
            "enrichment_id": enrichment_id,
            "enrichment_status": "pending",
            "reputation_score": 0.0,
            "error": None,
        }

    except Exception as e:
        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id,
            session_id=session_id_ctx.get(),
            event="domain_register_failed",
            payload={
                "domain_name": domain_name,
                "error": str(e),
            },
        )

        log_event(
            logger,
            level=40,
            event="domain_create_error",
            message="Error creando dominio",
            extra={"domain": domain_name, "error": str(e)},
            exc_info=True,
        )
        db.rollback()
        return {
            "domain_id": None,
            "domain_name": domain_name,
            "created": False,
            "enrichment_id": None,
            "enrichment_status": "error",
            "error": str(e),
        }


def get_domain_by_name(domain_name: str, *, db: Session) -> Domain | None:
    """
    Obtiene un dominio por nombre.

    Args:
        domain_name(str): Nombre del dominio
        db(Session): Sesión de BD

    Returns:
        Domain | None: Registro del dominio o None
    """
    return db.query(Domain).filter(Domain.domain_name == domain_name).first()


def get_domain_enrichment(domain_id: str, *, db: Session) -> DomainEnrichment | None:
    """
    Obtiene los datos de enriquecimiento de un dominio.

    Args:
        domain_id(str): ID del dominio
        db(Session): Sesión de BD

    Returns:
        DomainEnrichment | None: Datos de enriquecimiento o None
    """
    return db.query(DomainEnrichment).filter(DomainEnrichment.domain_id == domain_id).first()


def list_user_domains(user_id: str, status: str | None = None, *, db: Session) -> list[dict]:
    """
    Lista los dominios de un usuario.

    Args:
        user_id(str): ID del usuario
        status(str | None): Filtrar por estado ("activo", "inactivo") o None para todos
        db(Session): Sesión de BD

    Returns:
        list[dict]: Lista de dominios con datos básicos
    """
    query = db.query(Domain).filter(Domain.user_id == user_id)

    if status:
        query = query.filter(Domain.status == status)

    domains = query.all()

    result = []
    for domain in domains:
        enrichment = get_domain_enrichment(domain.id, db=db)
        result.append({
            "id": domain.id,
            "domain_name": domain.domain_name,
            "status": domain.status,
            "tags": domain.tags,
            "created_at": domain.created_at,
            "reputation_score": enrichment.reputation_score if enrichment else 0.0,
            "expiration_date": enrichment.whois_expiration_date if enrichment else None,
        })

    return result


def delete_domain(domain_id: str, user_id: str, *, db: Session) -> dict[str, Any]:
    """
    Elimina un dominio y su enrichment asociado

    Args:
        domain_id(str): ID del dominio a eliminar
        user_id(str): ID del usuario propietario verificacando su pertenencia
        db(Session): Sesión de BD

    Returns:
        dict[str, Any]: Resultado con deleted=True/False
    """
    try:
        domain = db.query(Domain).filter(
            Domain.id == domain_id,
            Domain.user_id == user_id,
        ).first()

        if not domain:
            return {"deleted": False, "error": "Dominio no encontrado o no pertenece al usuario."}

        domain_name = domain.domain_name
        db.delete(domain)
        db.commit()

        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id,
            session_id=session_id_ctx.get(),
            event="domain_deleted",
            payload={"domain_id": domain_id, "domain_name": domain_name},
        )

        log_event(
            logger,
            level=20,
            event="domain_delete_complete",
            message="Dominio eliminado",
            extra={"domain_id": domain_id, "domain": domain_name},
        )
        return {"deleted": True, "domain_name": domain_name}

    except Exception as e:
        db.rollback()
        log_event(
            logger,
            level=40,
            event="domain_delete_error",
            message="Error eliminando dominio",
            extra={"domain_id": domain_id, "error": str(e)},
            exc_info=True,
        )
        return {"deleted": False, "error": str(e)}


def update_domain(
    domain_id: str,
    user_id: str,
    *,
    tags: list[str] | None = None,
    status: str | None = None,
    db: Session,
) -> dict[str, Any]:
    """
    Actualiza tags y/o estado de un dominio

    Args:
        domain_id(str): ID del dominio
        user_id(str): ID del usuario propietario
        tags(list[str] | None): Nuevas etiquetas, o None para no cambiar
        status(str | None): Nuevo estado ("activo"/"inactivo"), o None para no cambiar
        db(Session): Sesión de BD

    Returns:
        dict[str, Any]: Resultado con updated=True/False
    """
    try:
        domain = db.query(Domain).filter(
            Domain.id == domain_id,
            Domain.user_id == user_id,
        ).first()

        if not domain:
            return {"updated": False, "error": "Dominio no encontrado o no pertenece al usuario."}

        if tags is not None:
            domain.tags = tags
        if status is not None:
            domain.status = status

        db.commit()

        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id,
            session_id=session_id_ctx.get(),
            event="domain_updated",
            payload={
                "domain_id": domain_id,
                "domain_name": domain.domain_name,
                "tags": tags,
                "status": status,
            },
        )

        log_event(
            logger,
            level=20,
            event="domain_update_complete",
            message="Dominio actualizado",
            extra={"domain_id": domain_id, "domain": domain.domain_name},
        )
        return {
            "updated": True,
            "domain_id": domain_id,
            "domain_name": domain.domain_name,
            "tags": domain.tags,
            "status": domain.status,
        }

    except Exception as e:
        db.rollback()
        log_event(
            logger,
            level=40,
            event="domain_update_error",
            message="Error actualizando dominio",
            extra={"domain_id": domain_id, "error": str(e)},
            exc_info=True,
        )
        return {"updated": False, "error": str(e)}
