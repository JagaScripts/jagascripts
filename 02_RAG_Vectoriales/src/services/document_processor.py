import os
import uuid # Generación de IDs únicos para los puntos vectoriales
import qdrant_client
from qdrant_client.http import models
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from pydantic import BaseModel
from typing import List
from src.config import settings

# Cliente síncrono para operaciones de gestión de colecciones y filtrado previo
qdrant_client_sync = qdrant_client.QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=60)

# Configuración del modelo de embeddings de Google (Gemini 1.0)
embed_model = GoogleGenAIEmbedding(model_name=settings.EMBEDDING_MODEL, api_key=settings.GEMINI_API_KEY)
# Parser para fragmentar el texto en bloques (chunks) manejables
node_parser = SentenceSplitter(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)

async def process_and_ingest_document(doc_id: str, title: str, category: str, text: str) -> int:
    try:
        qdrant_client_sync.get_collection(settings.COLLECTION_NAME)
    except Exception:
        qdrant_client_sync.create_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config=models.VectorParams(size=3072, distance=models.Distance.COSINE),
        )

    # --- Lógica de Soft Delete (Gestión de Obsolescencia) ---
    # Buscamos fragmentos existentes con el mismo doc_id que estén marcados como 'active'
    filter_condition = Filter(
        must=[
            FieldCondition(key="doc_id", match=MatchValue(value=doc_id)),
            FieldCondition(key="status", match=MatchValue(value="active"))
        ]
    )
    # Scroll para localizar todos los puntos previos antes de archivarlos
    points_to_update = qdrant_client_sync.scroll(
        collection_name=settings.COLLECTION_NAME,
        scroll_filter=filter_condition,
        limit=10000
    )
    
    # Si existen versiones previas, actualizamos su estado a 'archived'
    if points_to_update and len(points_to_update[0]) > 0:
        for point in points_to_update[0]:
            qdrant_client_sync.set_payload(
                collection_name=settings.COLLECTION_NAME,
                payload={"status": "archived"},
                points=[point.id]
            )

    doc = Document(text=text, metadata={"doc_id": doc_id, "title": title, "category": category, "status": "active"})
    nodes = node_parser.get_nodes_from_documents([doc])
    
    points_to_insert = []
    vector_dim = 3072 # Dimensión de salida del modelo gemini-embedding-001
    for node in nodes:
        # Modo de prueba: Si no hay API Key real, generamos vectores ficticios
        if settings.GEMINI_API_KEY == "dummy_key_for_testing" or not settings.GEMINI_API_KEY:
            node.embedding = [0.1] * vector_dim
        else:
            # Generación de embeddings reales usando la API de Google de forma asíncrona
            node.embedding = await embed_model.aget_text_embedding(node.get_content())
            
        points_to_insert.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=node.embedding,
            payload={
                "doc_id": doc_id,
                "title": title,
                "category": category,
                "status": "active",
                "text": node.get_content()
            }
        ))
        
    if points_to_insert:
        qdrant_client_sync.upsert(
            collection_name=settings.COLLECTION_NAME,
            points=points_to_insert
        )
    
    return len(nodes)
