from __future__ import annotations
import uuid
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.settings import settings
from app.orchestrator.engine import run_orchestrator

router = APIRouter()


class OrchestrateRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=30)
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=120)
    context: dict = Field(default_factory=dict)


class OrchestrateResponse(BaseModel):
    final_user_message: str
    session_id: str
    show_menu: bool = False


# Endpoint interno del orquestador
@router.post("/orchestrate", response_model=OrchestrateResponse)
def orchestrate(req: OrchestrateRequest) -> OrchestrateResponse:
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:10]}"
    out = run_orchestrator(
        user_id=req.user_id,
        session_id=session_id,
        message=req.message,
        model=settings.openai_model,
    )
    return OrchestrateResponse(
        final_user_message=out["final_user_message"],
        session_id=session_id,
        show_menu=bool(out.get("show_menu", False)),
    )
