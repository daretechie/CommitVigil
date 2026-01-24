from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "CommitGuard AI"}

@patch("src.main.create_pool")
def test_evaluate_commitment_enqueued(mock_create_pool):
    # Mock the Redis pool and enqueue_job
    mock_redis = AsyncMock()
    mock_create_pool.return_value = mock_redis
    
    payload = {
        "user_id": "test_user",
        "commitment": "Write more tests",
        "check_in": "I am working on it"
    }
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "enqueued"
    
    # Verify Redis was actually called
    mock_create_pool.assert_called_once()
    mock_redis.enqueue_job.assert_called_once()


def test_ingest_raw_commitment():
    response = client.post(
        "/ingest/raw", 
        params={"user_id": "api_test_user", "raw_text": "I'll finish the docs by Friday"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "extracted"
    assert "owner" in response.json()

