import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from src.api.routes import router
from fastapi import FastAPI
from src.schemas.performance import SlippageAnalysis, TruthGapAnalysis
from src.core.config import settings

# Setup a minimal test app
app = FastAPI()
app.include_router(router, prefix="/api/v1")


@pytest.fixture
def mock_dependencies():
    with (
        patch(
            "src.api.routes.get_user_reliability", new_callable=AsyncMock
        ) as mock_rel,
        patch("src.api.routes.SlippageAnalyst", autospec=True) as mock_slippage,
        patch("src.api.routes.TruthGapDetector", autospec=True) as mock_truth,
    ):
        mock_rel.return_value = (85.5, 10, 2)

        # Mocking Analyst
        mock_slippage.return_value.analyze_performance_gap = AsyncMock(
            return_value=SlippageAnalysis(
                status="slipping",
                fulfillment_ratio=0.7,
                detected_gap="Missing refactor",
                risk_to_system_stability=0.5,
                intervention_required=True,
            )
        )

        # Mocking Detector
        mock_truth.return_value.detect_gap = AsyncMock(
            return_value=TruthGapAnalysis(
                gap_detected=True,
                truth_score=0.4,
                explanation="Commit history doesn't match claims.",
                recommended_tone="Firm",
            )
        )

        yield


@pytest.mark.asyncio
async def test_get_performance_audit_json(mock_dependencies):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/api/v1/reports/audit/test_user",
            headers={"X-API-Key": settings.API_KEY_SECRET},
        )
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert data["subject"]["reliability_score"] == "85.50%"


@pytest.mark.asyncio
async def test_get_performance_audit_markdown(mock_dependencies):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/api/v1/reports/audit/test_user?report_format=markdown",
            headers={"X-API-Key": settings.API_KEY_SECRET},
        )
    assert response.status_code == 200
    data = response.json()
    assert "# 🛡️ Performance Integrity Audit" in data["content"]


@pytest.mark.asyncio
async def test_get_performance_audit_html(mock_dependencies):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/api/v1/reports/audit/test_user?report_format=html",
            headers={"X-API-Key": "my-secure-api-key-12345"},
        )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "PERFORMANCE AUDIT" in response.text
