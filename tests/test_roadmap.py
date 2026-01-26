import pytest
from unittest.mock import patch, AsyncMock
from src.agents.brain import CommitGuardBrain
from src.agents.safety import SafetySupervisor
from src.agents.learning import SupervisorFeedbackLoop
from src.schemas.agents import ToneType, SafetyAudit, SafetyFeedback
from src.core.database import init_db

@pytest.fixture(autouse=True)
async def setup_db():
    """Ensure database is initialized and clean."""
    await init_db()
    from src.core.database import AsyncSessionLocal
    from sqlmodel import delete
    async with AsyncSessionLocal() as session:
        await session.execute(delete(SafetyFeedback))
        await session.commit()

@pytest.mark.asyncio
async def test_japanese_cultural_routing():
    """Verify that Japanese language triggers the correct cultural persona."""
    brain = CommitGuardBrain()
    
    # Mock language detection to return 'ja'
    with patch.object(brain, "detect_language", return_value="ja"):
        with patch.object(brain.provider, "chat_completion", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = AsyncMock() # Generic response
            
            await brain.adapt_tone(
                excuse=AsyncMock(),
                risk=AsyncMock(),
                burnout=AsyncMock(),
                lang="ja"
            )
            
            # Check if the Japanese cultural prompt was used
            called_prompt = mock_chat.call_args[1]["messages"][0]["content"]
            assert "High-context Japanese tone" in called_prompt
            assert "harmony (wa)" in called_prompt

@pytest.mark.asyncio
async def test_french_cultural_routing():
    """Verify that French language triggers the correct cultural persona."""
    brain = CommitGuardBrain()
    with patch.object(brain, "detect_language", return_value="fr"):
        with patch.object(brain.provider, "chat_completion", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = AsyncMock()
            await brain.adapt_tone(excuse=AsyncMock(), risk=AsyncMock(), burnout=AsyncMock(), lang="fr")
            called_prompt = mock_chat.call_args[1]["messages"][0]["content"]
            assert "French professional tone" in called_prompt
            assert "eloquence" in called_prompt

@pytest.mark.asyncio
async def test_british_english_routing():
    """Verify that UK English triggers polite understatements."""
    brain = CommitGuardBrain()
    # Explicitly asking for en-UK
    with patch.object(brain.provider, "chat_completion", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = AsyncMock()
        await brain.adapt_tone(excuse=AsyncMock(), risk=AsyncMock(), burnout=AsyncMock(), lang="en-UK")
        called_prompt = mock_chat.call_args[1]["messages"][0]["content"]
        assert "British professional tone" in called_prompt
        assert "understatements" in called_prompt

@pytest.mark.asyncio
async def test_hipaa_semantic_firewall_blocking():
    """Verify that HIPAA rules block PHI/PII semantically."""
    supervisor = SafetySupervisor()
    
    with patch.object(supervisor.provider, "chat_completion", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = SafetyAudit(
            is_safe=False,
            is_hard_blocked=True,
            risk_of_morale_damage=0.2,
            supervisor_confidence=0.9,
            reasoning="HIPAA Violation: Mentions Patient PHI",
            correction_type="none"
        )
        
        audit = await supervisor.audit_message(
            message="Please check the patient records for John Doe's treatment.",
            tone=ToneType.NEUTRAL,
            user_context="healthcare_app",
            industry="healthcare"
        )
        
        assert audit.is_hard_blocked is True
        assert "HIPAA" in audit.reasoning
        
        # Verify the system prompt was industry-specific
        system_msg = mock_chat.call_args[1]["messages"][0]["content"]
        assert "Healthcare Ethics" in system_msg

@pytest.mark.asyncio
async def test_feedback_loop_persistence():
    """Verify that manager feedback is actually persisted to the DB."""
    from src.schemas.agents import SafetyFeedback
    from sqlmodel import select
    from src.core.database import AsyncSessionLocal
    
    loop = SupervisorFeedbackLoop()
    
    await loop.log_manager_decision(
        intervention_id="int_123",
        user_id="dev_user",
        manager_id="mgr_456",
        action="accepted",
        message="Keep it up!",
        notes="Perfect correction."
    )
    
    async with AsyncSessionLocal() as session:
        statement = select(SafetyFeedback).where(SafetyFeedback.intervention_id == "int_123")
        result = await session.execute(statement)
        feedback = result.scalar_one_or_none()
        
        assert feedback is not None
        assert feedback.action_taken == "accepted"
        assert feedback.manager_id == "mgr_456"
