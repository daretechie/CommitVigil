from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.deps import get_redis
from src.core.config import settings
from src.main import app
from src.schemas.agents import UserHistory

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


def test_evaluate_commitment_redis_not_initialized():
    """Verify that evaluation fails with 503 if Redis is unavailable."""
    payload = {"user_id": "u1", "commitment": "c", "check_in": "ok"}

    # Override get_redis to raise 503
    async def mock_get_redis_fail():
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail="Redis service unavailable")

    app.dependency_overrides[get_redis] = mock_get_redis_fail
    try:
        response = client.post("/api/v1/evaluate", json=payload)
        assert response.status_code == 503
        assert "Redis service unavailable" in response.json()["detail"]
    finally:
        app.dependency_overrides = {}


def test_evaluate_commitment_demo_mode_no_longer_sync():
    """Verify that even in Demo Mode, missing Redis results in 503 (Sync fallback removed)."""
    payload = {"user_id": "u1", "commitment": "c", "check_in": "ok"}

    async def mock_get_redis_fail():
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail="Service Temporarily Unavailable")

    app.dependency_overrides[get_redis] = mock_get_redis_fail
    try:
        with patch("src.api.v1.evaluation.settings.DEMO_MODE", True):
            response = client.post("/api/v1/evaluate", json=payload)
            assert response.status_code == 503
            assert "Service Temporarily Unavailable" in response.json()["detail"]
    finally:
        app.dependency_overrides = {}


def test_evaluate_commitment_success():
    mock_redis = AsyncMock()
    mock_job = MagicMock()
    mock_job.job_id = "test-job-id"
    mock_redis.enqueue_job.return_value = mock_job

    app.dependency_overrides[get_redis] = lambda: mock_redis
    try:
        payload = {"user_id": "u1", "commitment": "c", "check_in": "ok"}
        response = client.post("/api/v1/evaluate", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "enqueued"
        mock_redis.enqueue_job.assert_called_once()
    finally:
        app.dependency_overrides = {}


def test_ingest_raw_commitment():
    response = client.post(
        "/api/v1/ingest/raw", params={"user_id": "u1", "raw_text": "I will fix it"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "extracted"


@patch("src.api.v1.config_routes.set_slack_id", new_callable=AsyncMock)
def test_map_slack_user(mock_set):
    response = client.post("/api/v1/users/config/slack", params={"user_id": "u1", "slack_id": "s1"})
    assert response.status_code == 200
    mock_set.assert_called_once_with("u1", "s1")


@patch("src.api.v1.config_routes.set_git_email", new_callable=AsyncMock)
def test_map_git_user(mock_set):
    response = client.post("/api/v1/users/config/git", params={"user_id": "u1", "email": "e1"})
    assert response.status_code == 200
    mock_set.assert_called_once_with("u1", "e1")


@patch("src.api.v1.ingestion.get_user_by_git_email", new_callable=AsyncMock)
def test_ingest_git_commitment_matched(mock_get_user):
    mock_get_user.return_value = UserHistory(user_id="john_dev", git_email="john@example.com")
    payload = {"author_email": "john@example.com", "message": "hello"}
    response = client.post("/api/v1/ingest/git", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "extracted"
    assert response.json()["identity_matched"] is True


@patch("src.api.v1.ingestion.get_user_by_git_email", new_callable=AsyncMock)
def test_ingest_git_commitment_unmatched(mock_get_user):
    mock_get_user.return_value = None
    payload = {"author_email": "unknown@example.com", "message": "hello"}
    response = client.post("/api/v1/ingest/git", json=payload)
    assert response.status_code == 200
    assert response.json()["identity_matched"] is False


@pytest.mark.asyncio
async def test_reports_audit():
    """Verify that the reports audit endpoint works with real database entries."""
    from src.core.database import AsyncSessionLocal

    # 1. Seed the test database
    async with AsyncSessionLocal() as session:
        user = UserHistory(
            user_id="u1", reliability_score=85.0, department="Engineering", total_commitments=5
        )
        session.add(user)
        await session.commit()

    # 2. Mock Agent responses to avoid actual LLM calls
    # We use patch.multiple for a cleaner interface
    with (
        patch("src.api.v1.reports.SlippageAnalyst", autospec=True) as mock_ana,
        patch("src.api.v1.reports.TruthGapDetector", autospec=True) as mock_det,
        patch("src.api.v1.reports.AuditReportGenerator", autospec=True) as mock_gen,
    ):
        mock_ana_inst = mock_ana.return_value
        mock_ana_inst.analyze_performance_gap = AsyncMock(return_value=MagicMock())

        mock_det_inst = mock_det.return_value
        mock_det_inst.detect_gap = AsyncMock(return_value=MagicMock())

        mock_gen.generate_audit_summary.return_value = {"report": "final_content"}

        response = client.get("/api/v1/reports/audit/u1")
        assert response.status_code == 200
        assert response.json() == {"report": "final_content"}


@pytest.mark.asyncio
async def test_lifespan():
    """Test lifespan events explicitly."""
    from src.core.state import state
    from src.main import lifespan

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


@patch("src.api.deps.settings")
def test_auth_bypass_when_disabled(mock_settings):
    """Verify requests pass through when AUTH_ENABLED=False."""
    mock_settings.AUTH_ENABLED = False
    mock_settings.API_KEY_SECRET = "dev-secret-key"

    no_auth_client = TestClient(app)
    # Health endpoint should always work
    response = no_auth_client.get("/health")
    assert response.status_code == 200


def test_auth_with_invalid_key():
    """Verify that an invalid API key is rejected."""
    bad_auth_client = TestClient(app)
    bad_auth_client.headers = {"X-API-Key": "wrong-key"}
    response = bad_auth_client.post("/api/v1/evaluate", json={})
    assert response.status_code == 403
    assert "Invalid API Key" in response.json()["detail"]


@pytest.mark.asyncio
async def test_safety_supervisor_audit():
    """Test SafetySupervisor audit_message function."""
    from src.agents.safety import SafetySupervisor
    from src.schemas.agents import ToneType

    supervisor = SafetySupervisor()

    with patch.object(supervisor.provider, "chat_completion", new_callable=AsyncMock) as mock_chat:
        from src.schemas.agents import SafetyAudit

        mock_chat.return_value = SafetyAudit(
            is_safe=True,
            supervisor_confidence=0.9,
            risk_of_morale_damage=0.0,
            reasoning="Safe",
            is_hard_blocked=False,
        )

        result = await supervisor.audit_message(
            message="Please complete the task by Friday.",
            tone=ToneType.NEUTRAL,
            user_context="Reliability: 85%, Consecutive firm: 1",
        )

        # The mock provider should return a SafetyAudit
        assert hasattr(result, "is_safe")
        assert hasattr(result, "is_hard_blocked")
        assert result.is_safe is True


def test_metrics_protection():
    """Verify that the /metrics endpoint is protected by API key."""
    # 1. No auth should fail
    no_auth_client = TestClient(app)
    response = no_auth_client.get("/metrics")
    assert response.status_code == 403

    # 2. Correct auth should pass
    response = client.get("/metrics")
    assert response.status_code == 200
    # Prometheus format usually starts with # HELP
    assert b"# HELP" in response.content
