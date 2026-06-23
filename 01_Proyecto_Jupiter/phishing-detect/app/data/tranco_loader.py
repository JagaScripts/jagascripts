from __future__ import annotations

import csv
import io
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from app.core.logging import get_logger

logger = get_logger("tranco_loader")

_TRANCO_URL = "https://tranco-list.eu/top-1m.csv.zip"
_CACHE_FILE = Path(__file__).parent / "tranco_top10k.csv"
_MAX_AGE_DAYS = 7


def _is_stale() -> bool:
    """ Devuelve True si el archivo no existe o tiene más de 7 días """
    if not _CACHE_FILE.exists():
        return True
    mtime = datetime.fromtimestamp(_CACHE_FILE.stat().st_mtime, tz=timezone.utc)
    return datetime.now(timezone.utc) - mtime > timedelta(days=_MAX_AGE_DAYS)


def refresh_tranco_list() -> bool:
    """Descarga la lista Tranco top 100.000 si está desactualizada.

    Returns(bool): True si se descargó correctamente, False si falló.
    """
    if not _is_stale():
        logger.info("Lista Tranco en caché, no requiere actualización")
        return True

    logger.info("Descargando lista Tranco top 100.000 ...")
    try:
        response = requests.get(_TRANCO_URL, timeout=30)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            csv_name = next(n for n in z.namelist() if n.endswith(".csv"))
            csv_content = z.read(csv_name).decode("utf-8")

        _CACHE_FILE.write_text(csv_content, encoding="utf-8")
        logger.info("Lista Tranco descargada correctamente", extra={"event": "tranco_refreshed"})
        return True

    except Exception as e:
        logger.error(
            f"Error al descargar lista Tranco: {e}",
            extra={"event": "tranco_download_error", "error": str(e)},
            exc_info=True,
        )
        return False


def load_tranco_domains() -> list[str]:
    """Carga los dominios de la lista Tranco cacheada

    Returns(list[str]): Lista de dominios en formato 'example.com'.
    """
    if not _CACHE_FILE.exists():
        logger.warning("Archivo Tranco no encontrado, usando lista vacía")
        return []

    domains: list[str] = []
    try:
        with _CACHE_FILE.open(encoding="utf-8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i >= 100000:  # para el MVP vamos a usar solo 100k dominios
                    break
                if len(row) >= 2:
                    domains.append(row[1].strip().lower())
    except Exception as e:
        logger.error(
            f"Error al leer lista Tranco: {e}",
            extra={"event": "tranco_load_error", "error": str(e)},
            exc_info=True,
        )

    return domains
