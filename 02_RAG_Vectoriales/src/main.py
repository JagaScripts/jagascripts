from fastapi import FastAPI
from src.api.ingest import router as ingest_router
from src.api.search import router as search_router

app = FastAPI(title="Jupiter Phishing Detect - RAG Engine", version="1.0.0")

app.include_router(ingest_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
