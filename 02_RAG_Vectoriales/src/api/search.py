from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from src.services.search_processor import perform_search

router = APIRouter()

class SourceNode(BaseModel):
    text: str
    metadata: dict
    score: float

class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    response: str
    sources: List[SourceNode]

# Procesa la pregunta del usuario y recupera información únicamente del contexto activo
@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        response_text, sources = await perform_search(request.query)
        return SearchResponse(response=response_text, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
