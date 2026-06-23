from __future__ import annotations
import uuid
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.orchestrator.engine import run_orchestrator
from app.core.logging import trace_id_ctx
from app.core.settings import settings


router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=80)
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=120)


class ChatResponse(BaseModel):
    session_id: str
    trace_id: str
    assistant_message: str
    show_menu: bool = False


# Endpoint para interactuar con el chat
@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """
    Funcion para interactuar con el agente orquestador

    Args:
        req: Elemento de la clase ChatRequest que lleva el user_id, el mensaje del usuario y el session_id

    Return:
        Devuelve la contestación del agente orquestador, el session_id, trace_id y si debe mostrar el menú
    """
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:10]}"
    trace_id = trace_id_ctx.get() or "-"

    out = run_orchestrator(user_id=req.user_id, session_id=session_id, message=req.message, model=settings.openai_model)

    return ChatResponse(
        session_id=session_id,
        trace_id=trace_id,
        assistant_message=out.get("final_user_message", ""),
        show_menu=bool(out.get("show_menu", False)),
    )
