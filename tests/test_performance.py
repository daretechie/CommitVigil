from unittest.mock import patch, AsyncMock
import pytest
from src.agents.performance import SlippageAnalyst, TruthGapDetector
from src.schemas.performance import SlippageStatus

@pytest.mark.asyncio
async def test_slippage_analyst_mock():
    analyst = SlippageAnalyst(provider_name="mock")
    analysis = await analyst.analyze_performance_gap(
        promised_tasks=["Refactor DB"],
        actual_work_done="Fixed some typos"
    )
    assert analysis.fulfillment_ratio == 0.9
    assert analysis.status == SlippageStatus.ON_TRACK

@pytest.mark.asyncio
async def test_truth_gap_detector_mock():
    detector = TruthGapDetector(provider_name="mock")
    analysis = await detector.detect_gap(
        check_in_text="I'm 90% done",
        technical_evidence="0 lines changed"
    )
    assert analysis.gap_detected is False
    assert analysis.truth_score == 0.95
