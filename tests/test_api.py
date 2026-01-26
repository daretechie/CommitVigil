from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.core.config import settings

# Inject Auth Header Globally for Tests
client = TestClient(app)
client.headers = {"X-API-Key": settings.API_KEY_SECRET}


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]


def test_auth_enforcement():
    """Verify that missing auth token results in 403."""
    no_auth_client = TestClient(app)
    # Try a protected endpoint
    response = no_auth_client.post("/api/v1/evaluate", json={})
    assert response.status_code == 403


def test_read_health_healthy():
    with patch("src.main.engine") as mock_engine, patch("src.main.state") as mock_state:
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
    with patch("src.main.engine") as mock_engine, patch("src.main.state") as mock_state:
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
    with patch("src.main.engine") as mock_engine, patch("src.main.state") as mock_state:
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


@patch("src.api.routes.state")
def test_evaluate_commitment_redis_not_initialized(mock_state):
    # Ensure state["redis"] returns None
    mock_state.__getitem__.return_value = None
    payload = {"user_id": "u1", "commitment": "c", "check_in": "ok"}
    response = client.post("/api/v1/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "error"


@patch("src.api.routes.state")
def test_evaluate_commitment_success(mock_state):
    mock_redis = AsyncMock()
    mock_job = MagicMock()
    mock_job.job_id = "test-job-id"
    mock_redis.enqueue_job.return_value = mock_job
    # Ensure state["redis"] returns our mock
    mock_state.__getitem__.return_value = mock_redis
    payload = {"user_id": "u1", "commitment": "c", "check_in": "ok"}
    response = client.post("/api/v1/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "enqueued"
    mock_redis.enqueue_job.assert_called_once()


def test_ingest_raw_commitment():
    response = client.post(
        "/api/v1/ingest/raw", params={"user_id": "u1", "raw_text": "I will fix it"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "extracted"


@patch("src.api.routes.set_slack_id", new_callable=AsyncMock)
def test_map_slack_user(mock_set):
    response = client.post(
        "/api/v1/users/config/slack", params={"user_id": "u1", "slack_id": "s1"}
    )
    assert response.status_code == 200
    mock_set.assert_called_once_with("u1", "s1")


@patch("src.api.routes.set_git_email", new_callable=AsyncMock)
def test_map_git_user(mock_set):
    response = client.post(
        "/api/v1/users/config/git", params={"user_id": "u1", "git_email": "e1"}
    )
    assert response.status_code == 200
    mock_set.assert_called_once_with("u1", "e1")


@patch("src.api.routes.get_user_by_git_email", new_callable=AsyncMock)
def test_ingest_git_commitment_matched(mock_get_user):
    mock_get_user.return_value = MagicMock(user_id="u1")
    payload = {"author_email": "e1", "message": "fixed bug"}
    response = client.post("/api/v1/ingest/git", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "extracted"
    assert response.json()["identity_matched"] is True


@patch("src.api.routes.get_user_by_git_email", new_callable=AsyncMock)
def test_ingest_git_commitment_unmatched(mock_get_user):
    mock_get_user.return_value = None
    payload = {"author_email": "unknown", "message": "hello"}
    response = client.post("/api/v1/ingest/git", json=payload)
    assert response.status_code == 200
    assert response.json()["identity_matched"] is False


@patch("src.api.routes.get_user_reliability", new_callable=AsyncMock)
@patch("src.api.routes.SlippageAnalyst")
@patch("src.api.routes.TruthGapDetector")
@patch("src.api.routes.AuditReportGenerator")
def test_reports_audit(mock_gen, mock_det, mock_ana, mock_get_rel):
    mock_get_rel.return_value = (90.0, "s1", 0)

    mock_ana_inst = mock_ana.return_value
    mock_ana_inst.analyze_performance_gap = AsyncMock(return_value={})
    mock_det_inst = mock_det.return_value
    mock_det_inst.detect_gap = AsyncMock(return_value={})
    mock_gen.generate_audit_summary.return_value = {"report": "content"}

    response = client.get("/api/v1/reports/audit/u1")
    assert response.status_code == 200
    assert response.json() == {"report": "content"}


@pytest.mark.asyncio
async def test_lifespan():
    """Test lifespan events explicitly."""
    from src.main import lifespan
    from src.core.state import state
    
    mock_app = MagicMock()
    with (
        patch("src.main.init_db", new_callable=AsyncMock) as mock_db,
        patch("src.main.create_pool", new_callable=AsyncMock) as mock_redis,
    ):
        mock_redis_inst = AsyncMock()
        mock_redis.return_value = mock_redis_inst

        async with lifespan(mock_app):
            mock_db.assert_called_once()
            mock_redis.assert_called_once()
            assert state["redis"] == mock_redis_inst

        mock_redis_inst.close.assert_called_once()
        # Clean up global state after test
        state["redis"] = None
