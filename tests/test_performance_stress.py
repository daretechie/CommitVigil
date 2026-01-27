import asyncio
import time
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.brain import CommitVigilBrain
from src.schemas.agents import (
    AgentDecision,
    ToneType,
    ExcuseAnalysis,
    ExcuseCategory,
    RiskAssessment,
    RiskLevel,
    BurnoutDetection,
)


@pytest.fixture
def mock_brain_components():
    """Setup standard decision mocked components (Duplicated for isolation)"""
    decision = AgentDecision(
        action="notified",
        tone=ToneType.FIRM,
        message="Proposed Message",
        analysis_summary="sum",
    )
    excuse = ExcuseAnalysis(
        category=ExcuseCategory.LEGITIMATE, confidence_score=0.9, reasoning="logic"
    )
    risk = RiskAssessment(
        risk_score=0.1,
        level=RiskLevel.LOW,
        predicted_latency_days=0,
        mitigation_strategy="none",
    )
    burnout = BurnoutDetection(
        is_at_risk=False, sentiment_indicators=[], recommendation="rest"
    )
    return decision, excuse, risk, burnout


@pytest.mark.asyncio
async def test_concurrent_safety_checks(mock_brain_components):
    """
    Validation 2.0: Concurrent Load Testing.
    Simulate 50 simultaneous message audits to verify non-blocking IO and latency.
    """
    decision, excuse, risk, burnout = mock_brain_components

    # Setup Brain
    brain = CommitVigilBrain()
    brain.analyze_excuse = AsyncMock(return_value=excuse)
    brain.detect_burnout = AsyncMock(return_value=burnout)
    brain.assess_risk = AsyncMock(return_value=risk)
    brain.detect_language = AsyncMock(return_value="en")

    # Mock ToneAdapter
    msg = decision.model_copy()
    msg.message = "Check the logs."
    brain.adapt_tone = AsyncMock(return_value=msg)

    # Mock Supervisor with random delays (simulation of network/LLM latency)
    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value

        # Configure the mock to sleep slightly to verify concurrency
        async def mock_audit_with_delay(_msg, _tone, _ctx, industry="generic"):
            await asyncio.sleep(0.01)  # 10ms delay per call

            from src.agents.safety import SafetyAudit

            return SafetyAudit(
                is_safe=True,
                is_hard_blocked=False,
                supervisor_confidence=0.99,
                risk_of_morale_damage=0.0,
                correction_type="none",
                reasoning="Concurrent test pass",
            )

        mock_instance.audit_message = AsyncMock(side_effect=mock_audit_with_delay)

        # EXECUTION: 50 concurrent requests
        start_time = time.perf_counter()

        tasks = [
            brain.evaluate_participation("u1", "status", 100.0, 0) for _ in range(50)
        ]

        results = await asyncio.gather(*tasks)

        total_duration = time.perf_counter() - start_time

        print(
            f"\n[Load Test] Processed {len(results)} messages in {total_duration:.2f}s"
        )
        print(
            f"[Load Test] Effective Throughput: {len(results) / total_duration:.1f} msg/sec"
        )

        # ASSERTIONS
        assert len(results) == 50
        # If it were sequential (0.01 * 50) it would take >0.5s.
        # Concurrent should be much faster (approaching max(delay)).
        # We'll be generous with 0.2s to account for overhead.
        assert total_duration < 0.2, (
            f"Concurrency failed! Duration: {total_duration}s > 0.2s"
        )
        assert all(r.safety_audit is None for r in results)
