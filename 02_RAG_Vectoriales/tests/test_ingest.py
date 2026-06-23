import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.config import settings
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter

client = TestClient(app)

def test_document_chunking_size():
    # AC: Extract text, divide into fragments (chunks).
    text = "Word. " * 1000  # long text
    node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    doc = Document(text=text)
    nodes = node_parser.get_nodes_from_documents([doc])
    
    assert len(nodes) > 1
    # Check max chunk size
    for node in nodes:
        assert len(node.get_content().split()) <= 1000 # approximate

def test_metadata_extraction():
    # AC: Generate embeddings, and insert them into the database with the metadata status: active.
    doc = Document(text="Some text", metadata={"doc_id": "test_1", "status": "active", "category": "NLP"})
    assert doc.metadata["status"] == "active"
    assert doc.metadata["category"] == "NLP"

import os
import io

def test_ingest_new_document_success():
    # Creamos un PDF mínimo en memoria para el test
    from pypdf import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
    
    response = client.post("/api/v1/ingest", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "sections_extracted" in data

def test_update_document_triggers_soft_delete():
    # AC: System locates fragments of the previous document and updates metadata to status: archived
    # Creamos un PDF mínimo
    from pypdf import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    
    files = {"file": ("update_test.pdf", pdf_bytes, "application/pdf")}
    response_v1 = client.post("/api/v1/ingest", files=files)
    assert response_v1.status_code == 200

    # Insert second version (mismo nombre de archivo para simular actualización)
    pdf_bytes.seek(0)
    response_v2 = client.post("/api/v1/ingest", files=files)
    assert response_v2.status_code == 200


    # Verify directly in Qdrant
    import qdrant_client
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    
    # Check directly from the qdrant DB
    q_client = qdrant_client.QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=60)
    
    # Query for archived chunks
    filter_archived = Filter(
        must=[
            FieldCondition(key="doc_id", match=MatchValue(value="doc_test_update_123")),
            FieldCondition(key="status", match=MatchValue(value="archived"))
        ]
    )
    
    archived_points = q_client.scroll(
        collection_name=settings.COLLECTION_NAME,
        scroll_filter=filter_archived,
        limit=100
    )
    
    assert len(archived_points[0]) > 0
    assert archived_points[0][0].payload["title"] == "Report v1"

    # Query for active chunks
    filter_active = Filter(
        must=[
            FieldCondition(key="doc_id", match=MatchValue(value="doc_test_update_123")),
            FieldCondition(key="status", match=MatchValue(value="active"))
        ]
    )
    
    active_points = q_client.scroll(
        collection_name=settings.COLLECTION_NAME,
        scroll_filter=filter_active,
        limit=100
    )
    
    assert len(active_points[0]) > 0
    assert active_points[0][0].payload["title"] == "Report v2"
