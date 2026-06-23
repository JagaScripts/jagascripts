from __future__ import annotations

import json
from typing import Any

from app.storage.redis_client import get_redis

# TTL para limpiar drafts olvidados (2h)
_DRAFT_TTL_SECONDS = 2 * 60 * 60
_KEY_PREFIX = "phishing:rule_draft"


def _key(session_id: str) -> str:
    return f"{_KEY_PREFIX}:{session_id}"


def get_rule_draft(user_id: str, session_id: str) -> dict[str, Any]:
    """
    Recupera el borrador de regla asociado a una sesión

    Args:
        user_id(Str): Identificador de usuario
        session_id(str): Identificador de la sesión

    Returns:
        dict[str, Any]: Borrador actual de la regla o diccionario vacío
    """
    raw = get_redis().get(_key(session_id))
    if raw is None:
        return {"session_id": session_id, "user_id": user_id, "draft": {}}

    data = json.loads(raw)
    if data.get("user_id") != user_id:
        raise ValueError("session_id pertenece a otro user_id")

    return {"session_id": session_id, "user_id": user_id, "draft": data.get("draft", {})}


def upsert_rule_draft(user_id: str, session_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    """
    Crea o actualiza el borrador de una regla para una sesión

    Args:
        session_id(str): Identificador de la sesión
        user_id(str): Identificador del usuario
        patch(dict[str, Any]): Cambios parciales a aplicar al borrador

    Returns:
        dict[str, Any]: Borrador actualizado de la regla
    """
    r = get_redis()
    raw = r.get(_key(session_id))

    if raw is None:
        data = {"user_id": user_id, "session_id": session_id, "draft": {}}
    else:
        data = json.loads(raw)
        if data.get("user_id") != user_id:
            raise ValueError("session_id pertenece a otro user_id")

    data["draft"].update(patch)
    r.setex(_key(session_id), _DRAFT_TTL_SECONDS, json.dumps(data))
    return data["draft"].copy()


def clear_rule_draft(user_id: str, session_id: str) -> None:
    """Elimina el borrador de regla asociado a una sesión."""
    r = get_redis()
    raw = r.get(_key(session_id))
    if raw is None:
        return
    data = json.loads(raw)
    if data.get("user_id") != user_id:
        raise ValueError("session_id pertenece a otro user_id")
    r.delete(_key(session_id))
