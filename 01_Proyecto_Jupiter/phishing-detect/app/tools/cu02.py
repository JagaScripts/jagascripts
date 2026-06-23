from __future__ import annotations
import re
from typing import Any
from sqlalchemy.orm import Session
from app.services.domain_management import (
    create_domain,
    get_domain_by_name,
    get_domain_enrichment,
    list_user_domains as list_domains_service,
    delete_domain,
    update_domain,
)
from app.storage.audit_store import write_audit_event
from app.core.logging import trace_id_ctx, session_id_ctx
from app.core.logging import get_logger

logger = get_logger("tools.cu02")

_DOMAIN_RE = re.compile(
    r"^(?:[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?"
    r"\.)+[a-zA-Z]{2,}$"
)


def _validate_domain_name(domain_name: str) -> dict[str, Any]:
    """
    Valida el formato de un nombre de dominio

    Args:
        domain_name(str): Nombre del dominio a validar

    Returns:
        dict[str, Any]: Devuelve si el dominio es válido o no y los motivos
    """
    issues: list[str] = []

    if not domain_name or not domain_name.strip():
        issues.append("El nombre de dominio no puede estar vacío.")
        return {"valid": False, "issues": issues}

    domain = domain_name.strip().lower()

    if len(domain) < 3 or len(domain) > 255:
        issues.append("El dominio debe tener entre 3 y 255 caracteres.")

    if not _DOMAIN_RE.match(domain):
        issues.append("Formato inválido. Ejemplo válido: ejemplo.com")

    return {"valid": len(issues) == 0, "issues": issues}


def register_domain(
    user_id: str,
    domain_name: str,
    tags: list[str] | None = None,
    status: str = "activo",
    *,
    db: Session,
) -> dict[str, Any]:
    """
    Registra un dominio y lanza el enriquecimiento (WHOIS, DNS, MX, reputación)

    Args:
        user_id(str): ID del usuario propietario.
        domain_name(str): Nombre del dominio.
        tags(list[str] | None): Etiquetas opcionales.
        status(str): "activo" o "inactivo".
        db(Session): Sesión de base de datos.

    Returns:
        dict[str, Any]: Resultado con domain_id, enrichment_status y reputation_score.
    """
    validation = _validate_domain_name(domain_name)
    if not validation["valid"]:
        return {
            "created": False,
            "domain_name": domain_name,
            "error": "; ".join(validation["issues"]),
        }

    existing = get_domain_by_name(domain_name.strip().lower(), db=db)
    if existing:
        logger.warning(
            f"Dominio duplicado rechazado: {domain_name}",
            extra={"event": "domain_duplicate_rejected", "domain": domain_name, "user_id": user_id},
        )
        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id,
            session_id=session_id_ctx.get(),
            event="domain_duplicate_rejected",
            payload={"domain_name": domain_name},
        )
        return {
            "created": False,
            "domain_name": domain_name,
            "error": f"El dominio '{domain_name}' ya está registrado.",
        }

    return create_domain(
        user_id=user_id,
        domain_name=domain_name.strip().lower(),
        tags=tags,
        status=status,
        db=db,
    )


# Esta funcion no se ha implementado para el MVP.
def get_domain_detail(
    user_id: str,
    domain_name: str,
    *,
    db: Session,
) -> dict[str, Any]:
    """
    Obtiene los detalles completos de un dominio con su enriquecimiento

    Args:
        user_id(str): ID del usuario
        domain_name(str): Nombre del dominio
        db(Session): Sesión de base de datos

    Returns:
        dict[str, Any]: Datos del dominio + WHOIS, DNS, MX y reputación.
    """
    domain = get_domain_by_name(domain_name.strip().lower(), db=db)

    if not domain or domain.user_id != user_id:
        return {"found": False, "domain_name": domain_name, "error": "Dominio no encontrado."}

    enrichment = get_domain_enrichment(domain.id, db=db)

    return {
        "found": True,
        "domain_id": domain.id,
        "domain_name": domain.domain_name,
        "status": domain.status,
        "tags": domain.tags,
        "created_at": domain.created_at,
        "enrichment": {
            "whois_registrar": enrichment.whois_registrar if enrichment else None,
            "whois_creation_date": enrichment.whois_creation_date if enrichment else None,
            "whois_expiration_date": enrichment.whois_expiration_date if enrichment else None,
            "whois_registrant": enrichment.whois_registrant if enrichment else None,
            "dns_a_records": enrichment.dns_a_records if enrichment else None,
            "dns_ns_records": enrichment.dns_ns_records if enrichment else None,
            "mx_servers": enrichment.mx_servers if enrichment else None,
            "virustotal_malicious": enrichment.virustotal_malicioso if enrichment else None,
            "virustotal_suspicious": enrichment.virustotal_sospechoso if enrichment else None,
            "reputation_score": enrichment.reputation_score if enrichment else 0.0,
            "last_enriched_at": enrichment.last_enriched_at if enrichment else None,
        } if enrichment else None,
    }


def list_user_domains(
    user_id: str,
    status: str | None = None,
    *,
    db: Session,
) -> dict[str, Any]:
    """
    Lista los dominios registrados por el usuario

    Args:
        user_id(str): ID del usuario.
        status(str | None): Filtrar por "activo" / "inactivo" o None para todos.
        db(Session): Sesión de base de datos.

    Returns:
        dict[str, Any]: Lista de dominios con score de reputación y fecha de expiración.
    """
    items = list_domains_service(user_id=user_id, status=status, db=db)
    return {"items": items, "count": len(items)}


def delete_domain_tool(
    user_id: str,
    domain_name: str,
    *,
    db: Session,
) -> dict[str, Any]:
    """
    Elimina un dominio del usuario por nombre

    Args:
        user_id(str): ID del usuario
        domain_name(str): Nombre del dominio a eliminar
        db(Session): Sesión de base de datos

    Returns:
        dict[str, Any]: Resultado con deleted=True/False
    """
    domain = get_domain_by_name(domain_name.strip().lower(), db=db)

    if not domain or domain.user_id != user_id:
        return {"deleted": False, "error": f"El dominio '{domain_name}' no existe o no te pertenece."}

    return delete_domain(domain_id=domain.id, user_id=user_id, db=db)


def update_domain_tool(
    user_id: str,
    domain_name: str,
    *,
    tags: list[str] | None = None,
    status: str | None = None,
    db: Session,
) -> dict[str, Any]:
    """
    Actualiza tags y/o estado de un dominio por nombre

    Args:
        user_id(str): ID del usuario
        domain_name(str): Nombre del dominio a actualizar
        tags(list[str] | None): Nuevas etiquetas o None para no cambiar
        status(str | None): Nuevo estado o None para no cambiar
        db(Session): Sesión de base de datos

    Returns:
        dict[str, Any]: Resultado con updated=True/False
    """
    if status is not None and status not in ("activo", "inactivo"):
        return {
            "updated": False,
            "error": f"Estado '{status}' no válido. Los valores permitidos son 'activo' o 'inactivo'.",
        }

    domain = get_domain_by_name(domain_name.strip().lower(), db=db)

    if not domain or domain.user_id != user_id:
        return {"updated": False, "error": f"El dominio '{domain_name}' no existe o no te pertenece."}

    if tags is None and status is None:
        return {"updated": False, "error": "No se especificó ningún cambio."}

    return update_domain(domain_id=domain.id, user_id=user_id, tags=tags, status=status, db=db)
