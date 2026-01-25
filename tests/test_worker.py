import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime
from src.worker import process_commitment_eval, send_follow_up, startup, shutdown
from src.schemas.agents import ExcuseAnalysis, ExcuseCategory, RiskAssessment, RiskLevel, BurnoutDetection, AgentDecision

@pytest.mark.asyncio
async def test_send_follow_up():
    """Test the send_follow_up wrapper function."""
    with patch("src.worker.SlackConnector.send_notification", new_callable=AsyncMock) as mock_send:
        await send_follow_up("user1", "hello", slack_id="U123")
        mock_send.assert_called_once_with("hello", slack_id="U123")

@pytest.mark.asyncio
async def test_process_commitment_eval_low_risk():
    """Test full pipeline when risk is low (no follow-up scheduled)."""
    mock_brain_instance = MagicMock()
    mock_brain_instance.analyze_excuse = AsyncMock(return_value=ExcuseAnalysis(
        category=ExcuseCategory.LEGITIMATE, confidence_score=0.9, reasoning="logic"
    ))
    mock_brain_instance.assess_risk = AsyncMock(return_value=RiskAssessment(
        risk_score=0.1, level=RiskLevel.LOW, predicted_latency_days=0, mitigation_strategy="none"
    ))
    mock_brain_instance.detect_burnout = AsyncMock(return_value=BurnoutDetection(
        is_at_risk=False, sentiment_indicators=[], recommendation="rest"
    ))
    mock_brain_instance.adapt_tone = AsyncMock(return_value=AgentDecision(
        action="notified", tone="supportive", message="ok", analysis_summary="sum"
    ))

    with patch("src.worker.CommitGuardBrain", return_value=mock_brain_instance), \
         patch("src.worker.get_user_reliability", new_callable=AsyncMock, return_value=(95.0, "U123")), \
         patch("src.worker.update_user_reliability", new_callable=AsyncMock) as mock_update, \
         patch("src.worker.scheduler") as mock_scheduler:
        
        ctx = {}
        await process_commitment_eval(ctx, "user1", "task1", "status1")
        
        mock_update.assert_called_once_with("user1", was_failure=False)
        mock_scheduler.add_job.assert_not_called()

@pytest.mark.asyncio
async def test_process_commitment_eval_high_risk():
    """Test full pipeline when risk is high (follow-up scheduled)."""
    mock_brain_instance = MagicMock()
    mock_brain_instance.analyze_excuse = AsyncMock(return_value=ExcuseAnalysis(
        category=ExcuseCategory.DEFLECTION, confidence_score=0.8, reasoning="logic"
    ))
    mock_brain_instance.assess_risk = AsyncMock(return_value=RiskAssessment(
        risk_score=0.8, level=RiskLevel.HIGH, predicted_latency_days=2, mitigation_strategy="nudge"
    ))
    mock_brain_instance.detect_burnout = AsyncMock(return_value=BurnoutDetection(
        is_at_risk=False, sentiment_indicators=[], recommendation="rest"
    ))
    mock_brain_instance.adapt_tone = AsyncMock(return_value=AgentDecision(
        action="warned", tone="firm", message="hurry", analysis_summary="sum"
    ))

    with patch("src.worker.CommitGuardBrain", return_value=mock_brain_instance), \
         patch("src.worker.get_user_reliability", new_callable=AsyncMock, return_value=(50.0, "U123")), \
         patch("src.worker.update_user_reliability", new_callable=AsyncMock) as mock_update, \
         patch("src.worker.scheduler") as mock_scheduler:
        
        ctx = {}
        await process_commitment_eval(ctx, "user1", "task1", "status1")
        
        mock_update.assert_called_once_with("user1", was_failure=True)
        mock_scheduler.add_job.assert_called_once()

@pytest.mark.asyncio
async def test_worker_lifecycle():
    """Test worker startup and shutdown logic."""
    with patch("src.worker.init_db", new_callable=AsyncMock) as mock_init, \
         patch("src.worker.scheduler") as mock_scheduler:
        
        await startup({})
        mock_init.assert_called_once()
        mock_scheduler.start.assert_called_once()
        
        await shutdown({})
        mock_scheduler.shutdown.assert_called_once()
