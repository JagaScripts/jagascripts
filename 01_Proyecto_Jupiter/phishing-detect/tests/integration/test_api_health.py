import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.fixture(scope="module")
def client():
    """
    TestClient con dependencias externas mockeadas.
    Evita conexión real a BD, Redis, Qdrant y APIs en CI.
    """
    with (
        patch("app.db.init_db.init_db"),
        patch("app.storage.audit_store.init_audit_db"),
        patch("app.sheduler.create_scheduler"),
        patch("app.services.rag_service.RAGService.ingest"),
        patch("app.data.tranco_loader.refresh_tranco_list"),
    ):
        from app.main import create_app
        app = create_app()
        yield TestClient(app)


class TestHealthEndpoint:
    def test_health_ok(self, client):
        response = client.get("/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestChatEndpoint:
    def test_chat_sin_payload_devuelve_422(self, client):
        response = client.post("/v1/chat", json={})
        assert response.status_code == 422

    def test_chat_menu_principal(self, client):
        with patch("app.orchestrator.engine.run_orchestrator") as mock_engine:
            mock_engine.return_value = {
                "assistant_message": "Bienvenido al sistema",
                "show_menu": True,
            }
            response = client.post("/v1/chat", json={
                "user_id": "test-user",
                "message": "hola",
                "session_id": "test-session",
            })
            assert response.status_code == 200
            data = response.json()
            assert "assistant_message" in data
