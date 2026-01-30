from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.agents.safety import SafetySupervisor
from src.api.v1.reports import router
from src.core.config import settings
from src.schemas.agents import ToneType

app = FastAPI()
app.include_router(router, prefix="/api/v1")


@pytest.mark.asyncio
async def test_safety_supervisor_dynamic_rules():
    """Cover the dynamic_safety_rules logic in safety.py."""
    supervisor = SafetySupervisor()

    mock_context = AsyncMock()
    mock_context.department = "hr"
    mock_context.dynamic_safety_rules = [
        AsyncMock(rule_name="TestRule", reasoning="TestReasoning", target_tokens=["secret"])
    ]

    # We don't care about the result, just hitting the lines
    with patch(
        "src.agents.learning.SupervisorFeedbackLoop.calculate_intervention_acceptance",
        return_value=0.5,
    ):
        result = await supervisor.audit_message(
            "test message",
            ToneType.FIRM,
            "test context",
            industry="generic",
            context_profile=mock_context,
        )
        assert result.supervisor_confidence > 0


@pytest.mark.asyncio
async def test_reports_api_feedback_logging():
    """Cover the log_safety_feedback endpoint in reports.py."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        feedback = {
            "intervention_id": "int_1",
            "user_id": "u1",
            "manager_id": "m1",
            "action_taken": "accepted",
            "final_message_sent": "fixed",
            "comments": "good",
        }
        response = await ac.post(
            "/api/v1/feedback/safety", json=feedback, headers={"X-API-Key": settings.API_KEY_SECRET}
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_reports_api_departmental_audit():
    """Cover departmental audit endpoint (including mock fallback logic)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/reports/department/engineering", headers={"X-API-Key": settings.API_KEY_SECRET}
        )
        assert response.status_code == 200

        # Test HTML format
        response_html = await ac.get(
            "/api/v1/reports/department/engineering?report_format=html",
            headers={"X-API-Key": settings.API_KEY_SECRET},
        )
        assert response_html.status_code == 200


@pytest.mark.asyncio
async def test_reports_api_organizational_audit():
    """Cover organizational audit endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/reports/organization?report_format=html",
            headers={"X-API-Key": settings.API_KEY_SECRET},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_reports_api_predict_roi():
    """Cover predict-roi endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/demo/predict-roi?team_size=50", headers={"X-API-Key": settings.API_KEY_SECRET}
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_scout_agent_logic():
    """Cover ContextScout sensing logic."""
    from src.agents.scout import ContextScout

    scout = ContextScout()

    # Test successful sense (provider is mocked by default in tests)
    profile = await scout.sense_context(["need to ship this feature", "deadline is tomorrow"])
    assert profile.industry is not None

    # Test exception handling
    with patch.object(scout.provider, "chat_completion", side_effect=Exception("LLM Fail")):
        profile_fail = await scout.sense_context(["some text"])
        assert "Automatic sensing failed" in profile_fail.reasoning
