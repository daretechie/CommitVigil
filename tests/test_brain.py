import pytest
from src.agents.brain import CommitGuardBrain
from src.llm.mock import MockProvider
from src.schemas.agents import ExcuseCategory, ToneType


@pytest.fixture
def mock_brain():
    """
    Returns a CommitGuardBrain forced into Mock mode for hermetic testing.
    """
    brain = CommitGuardBrain()
    brain.provider = MockProvider()
    return brain


@pytest.mark.asyncio
async def test_brain_analyze_excuse_legitimate(mock_brain):
    # Test keyword detection for "sick"
    analysis = await mock_brain.analyze_excuse("I was sick yesterday")
    assert analysis.category == ExcuseCategory.LEGITIMATE


@pytest.mark.asyncio
async def test_brain_analyze_excuse_burnout(mock_brain):
    # Test keyword detection for burnout
    analysis = await mock_brain.analyze_excuse("I am totally exhausted and cannot cope")
    assert analysis.category == ExcuseCategory.BURNOUT_SIGNAL


@pytest.mark.asyncio
async def test_brain_analyze_excuse_deflection(mock_brain):
    # Test default deflection
    analysis = await mock_brain.analyze_excuse("I just forgot about it")
    assert analysis.category == ExcuseCategory.DEFLECTION


@pytest.mark.asyncio
async def test_brain_adapt_tone_burnout(mock_brain):
    # Setup inputs
    excuse = await mock_brain.analyze_excuse("exhausted")
    risk = await mock_brain.assess_risk("history", "status")
    burnout = await mock_brain.detect_burnout("exhausted")

    decision = await mock_brain.adapt_tone(excuse, risk, burnout)
    assert decision.tone == ToneType.SUPPORTIVE
    assert "limit" in decision.message.lower()
    assert decision.action == "escalate_to_manager"


@pytest.mark.asyncio
async def test_brain_adapt_tone_deflection(mock_brain):
    # Setup inputs
    excuse = await mock_brain.analyze_excuse("I forgot")
    risk = await mock_brain.assess_risk("history", "status")
    burnout = await mock_brain.detect_burnout("I forgot")

    decision = await mock_brain.adapt_tone(excuse, risk, burnout, reliability_score=40.0)
    assert decision.tone == ToneType.FIRM
    assert "recovery" in decision.message.lower()



@pytest.mark.asyncio
async def test_brain_extract_commitment(mock_brain):
    raw_slack_text = "Hey John, I'll have the landing page finished by Monday morning."
    extracted = await mock_brain.extract_commitment(raw_slack_text)

    assert extracted.confidence_score >= 0.8
    assert "Mock Task" in extracted.task
    assert "Friday" in extracted.deadline
