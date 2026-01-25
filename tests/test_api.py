from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
import pytest
from src.main import app
from src.schemas.agents import UserHistory

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_read_health_healthy():
    with patch("src.main.engine") as mock_engine, \
         patch("src.main.state") as mock_state:
        
        # Database mock success
        mock_conn = AsyncMock()
        mock_engine.connect.return_value.__aenter__.return_value = mock_conn
        
        # Redis mock success
        mock_redis = AsyncMock()
        mock_state.__getitem__.return_value = mock_redis
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["dependencies"]["database"] == "healthy"
        assert data["dependencies"]["redis"] == "healthy"

def test_read_health_degraded():
    with patch("src.main.engine") as mock_engine, \
         patch("src.main.state") as mock_state:
        
        # Database mock failure
        mock_engine.connect.side_effect = Exception("DB Down")
        
        # Redis mock failure
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Redis Down")
        mock_state.__getitem__.return_value = mock_redis
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["dependencies"]["database"] == "unhealthy"
        assert data["dependencies"]["redis"] == "unhealthy"

def test_read_health_redis_not_initialized():
    with patch("src.main.engine") as mock_engine, \
         patch("src.main.state") as mock_state:
        
        # Database mock success
        mock_conn = AsyncMock()
        mock_engine.connect.return_value.__aenter__.return_value = mock_conn
        
        # Redis is None in state
        mock_state.__getitem__.return_value = None
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["dependencies"]["redis"] == "not_initialized"

@patch("src.main.state")
def test_evaluate_commitment_redis_not_initialized(mock_state):
    # Ensure state["redis"] returns None
    mock_state.__getitem__.return_value = None
    payload = {"user_id": "u1", "commitment": "c", "check_in": "ok"}
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "error"

@patch("src.main.state")
def test_evaluate_commitment_success(mock_state):
    mock_redis = AsyncMock()
    # Ensure state["redis"] returns our mock
    mock_state.__getitem__.return_value = mock_redis
    payload = {"user_id": "u1", "commitment": "c", "check_in": "ok"}
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "enqueued"
    mock_redis.enqueue_job.assert_called_once()

def test_ingest_raw_commitment():
    response = client.post(
        "/ingest/raw", 
        params={"user_id": "u1", "raw_text": "I will fix it"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "extracted"

@patch("src.main.set_slack_id", new_callable=AsyncMock)
def test_map_slack_user(mock_set):
    response = client.post("/users/config/slack", params={"user_id": "u1", "slack_id": "s1"})
    assert response.status_code == 200
    mock_set.assert_called_once_with("u1", "s1")

@patch("src.main.set_git_email", new_callable=AsyncMock)
def test_map_git_user(mock_set):
    response = client.post("/users/config/git", params={"user_id": "u1", "git_email": "e1"})
    assert response.status_code == 200
    mock_set.assert_called_once_with("u1", "e1")

@patch("src.main.get_user_by_git_email", new_callable=AsyncMock)
def test_ingest_git_commitment_matched(mock_get_user):
    mock_get_user.return_value = MagicMock(user_id="u1")
    payload = {"author_email": "e1", "message": "fixed bug"}
    response = client.post("/ingest/git", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "extracted"
    assert response.json()["identity_matched"] is True

@patch("src.main.get_user_by_git_email", new_callable=AsyncMock)
def test_ingest_git_commitment_unmatched(mock_get_user):
    mock_get_user.return_value = None
    payload = {"author_email": "unknown", "message": "hello"}
    response = client.post("/ingest/git", json=payload)
    assert response.status_code == 200
    assert response.json()["identity_matched"] is False

@patch("src.main.get_user_reliability", new_callable=AsyncMock)
@patch("src.main.SlippageAnalyst")
@patch("src.main.TruthGapDetector")
@patch("src.main.AuditReportGenerator")
def test_reports_audit(mock_gen, mock_det, mock_ana, mock_get_rel):
    mock_get_rel.return_value = (90.0, "s1")
    mock_ana_inst = mock_ana.return_value
    mock_ana_inst.analyze_performance_gap = AsyncMock(return_value={})
    mock_det_inst = mock_det.return_value
    mock_det_inst.detect_gap = AsyncMock(return_value={})
    mock_gen.generate_audit_summary.return_value = {"report": "content"}
    
    response = client.get("/reports/audit/u1")
    assert response.status_code == 200
    assert response.json() == {"report": "content"}

@pytest.mark.asyncio
async def test_lifespan():
    """Test lifespan events explicitly."""
    from src.main import lifespan, state
    mock_app = MagicMock()
    with patch("src.main.init_db", new_callable=AsyncMock) as mock_db, \
         patch("src.main.create_pool", new_callable=AsyncMock) as mock_redis:
        
        mock_redis_inst = AsyncMock()
        mock_redis.return_value = mock_redis_inst
        
        async with lifespan(mock_app):
            mock_db.assert_called_once()
            mock_redis.assert_called_once()
            assert state["redis"] == mock_redis_inst
        
        mock_redis_inst.close.assert_called_once()
        # Clean up global state after test
        state["redis"] = None
