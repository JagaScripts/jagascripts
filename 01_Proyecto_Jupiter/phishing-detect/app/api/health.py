from fastapi import APIRouter

router = APIRouter()

# Endpoint para saber el estado de la API


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
