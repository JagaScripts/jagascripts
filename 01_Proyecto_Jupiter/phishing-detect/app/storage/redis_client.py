from __future__ import annotations

import redis
from urllib.parse import urlparse

from app.core.settings import settings
from app.core.logging import get_logger

logger = get_logger("storage.redis_client")

_redis_client: redis.Redis | None = None


def _safe_host(url: str) -> str:
    """Extrae host:puerto de la URL sin exponer credenciales."""
    parsed = urlparse(url)
    return f"{parsed.hostname}:{parsed.port or 6379}"


def get_redis() -> redis.Redis:
    """
    Devuelve el cliente Redis singleton, inicializándolo si es necesario.

    Returns:
        redis.Redis: Cliente Redis configurado con ConnectionPool
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
        logger.info(
            "Cliente Redis inicializado",
            extra={"event": "redis_client_init", "host": _safe_host(settings.redis_url)},
        )
    return _redis_client
