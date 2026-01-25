from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.schemas.agents import (
    AgentDecision,
    BurnoutDetection,
    ExcuseAnalysis,
    ExcuseCategory,
    PipelineEvaluation,
    RiskAssessment,
    RiskLevel,
    ToneType,
)
from src.worker import process_commitment_eval, send_follow_up, shutdown, startup


@pytest.mark.asyncio
async def test_send_follow_up():
    """Test the send_follow_up wrapper function."""
    with patch(
        "src.worker.SlackConnector.send_notification", new_callable=AsyncMock
    ) as mock_send:
        await send_follow_up("user1", "hello", slack_id="U123")
        mock_send.assert_called_once_with("hello", slack_id="U123")


@pytest.mark.asyncio
async def test_process_commitment_eval_low_risk():
    """Test full pipeline when risk is low (no follow-up scheduled)."""
    mock_brain_instance = MagicMock()

    # Mock return object
    mock_eval = PipelineEvaluation(
        decision=AgentDecision(
            action="notified",
            tone=ToneType.SUPPORTIVE,
            message="ok",
            analysis_summary="sum",
        ),
        excuse=ExcuseAnalysis(
            category=ExcuseCategory.LEGITIMATE, confidence_score=0.9, reasoning="logic"
        ),
        risk=RiskAssessment(
            risk_score=0.1,
            level=RiskLevel.LOW,
            predicted_latency_days=0,
            mitigation_strategy="none",
        ),
        burnout=BurnoutDetection(
            is_at_risk=False, sentiment_indicators=[], recommendation="rest"
        ),
    )

    mock_brain_instance.evaluate_participation = AsyncMock(return_value=mock_eval)

    with (
        patch("src.worker.CommitGuardBrain", return_value=mock_brain_instance),
        patch(
            "src.worker.get_user_reliability",
            new_callable=AsyncMock,
            return_value=(95.0, "U123", 0),
        ),
        patch(
            "src.worker.update_user_reliability", new_callable=AsyncMock
        ) as mock_update,
        patch("src.worker.scheduler") as mock_scheduler,
    ):
        ctx = {}
        await process_commitment_eval(ctx, "user1", "task1", "status1")

        mock_update.assert_called_once_with(
            "user1", was_failure=False, tone_used=ToneType.SUPPORTIVE
        )
        mock_scheduler.add_job.assert_not_called()


@pytest.mark.asyncio
async def test_process_commitment_eval_high_risk():
    """Test full pipeline when risk is high (follow-up scheduled)."""
    mock_brain_instance = MagicMock()

    # Mock return object
    mock_eval = PipelineEvaluation(
        decision=AgentDecision(
            action="warned", tone=ToneType.FIRM, message="hurry", analysis_summary="sum"
        ),
        excuse=ExcuseAnalysis(
            category=ExcuseCategory.DEFLECTION, confidence_score=0.8, reasoning="logic"
        ),
        risk=RiskAssessment(
            risk_score=0.8,
            level=RiskLevel.HIGH,
            predicted_latency_days=2,
            mitigation_strategy="nudge",
        ),
        burnout=BurnoutDetection(
            is_at_risk=False, sentiment_indicators=[], recommendation="rest"
        ),
    )

    mock_brain_instance.evaluate_participation = AsyncMock(return_value=mock_eval)

    with (
        patch("src.worker.CommitGuardBrain", return_value=mock_brain_instance),
        patch(
            "src.worker.get_user_reliability",
            new_callable=AsyncMock,
            return_value=(50.0, "U123", 1),
        ),
        patch(
            "src.worker.update_user_reliability", new_callable=AsyncMock
        ) as mock_update,
        patch("src.worker.scheduler") as mock_scheduler,
    ):
        ctx = {}
        await process_commitment_eval(ctx, "user1", "task1", "status1")

        mock_update.assert_called_once_with(
            "user1", was_failure=True, tone_used=ToneType.FIRM
        )
        mock_scheduler.add_job.assert_called_once()


@pytest.mark.asyncio
async def test_worker_lifecycle():
    """Test worker startup and shutdown logic."""
    with (
        patch("src.worker.init_db", new_callable=AsyncMock) as mock_init,
        patch("src.worker.scheduler") as mock_scheduler,
    ):
        await startup({})
        mock_init.assert_called_once()
        mock_scheduler.start.assert_called_once()

        await shutdown({})
        mock_scheduler.shutdown.assert_called_once()
