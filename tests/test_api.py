from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "CommitGuard AI"}

def test_evaluate_commitment_enqueued():
    payload = {
        "user_id": "test_user",
        "commitment": "Write more tests",
        "check_in": "I am working on it"
    }
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "enqueued"

def test_ingest_raw_commitment():
    response = client.post(
        "/ingest/raw", 
        params={"user_id": "api_test_user", "raw_text": "I'll finish the docs by Friday"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "extracted"
    assert "owner" in response.json()

