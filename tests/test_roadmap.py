from unittest.mock import AsyncMock, patch

import pytest

from src.agents.brain import CommitVigilBrain
from src.agents.learning import SupervisorFeedbackLoop
from src.agents.safety import SafetySupervisor
from src.schemas.agents import LanguageResponse, SafetyAudit, ToneType

# Using shared setup_test_db fixture from conftest.py


@pytest.mark.asyncio
async def test_japanese_cultural_routing():
    from src.schemas.agents import CulturalPersona

    brain = CommitVigilBrain()

    # Mock dynamic persona lookup
    mock_persona = CulturalPersona(
        code="ja",
        name="Japanese",
        instruction="High-context Japanese tone... harmony (wa)...",
        is_verified=True,
    )
    with patch.object(brain, "detect_language", return_value="ja"):
        with patch.object(
            brain, "get_or_create_persona", new_callable=AsyncMock
        ) as mock_get_persona:
            mock_get_persona.return_value = mock_persona

            with patch.object(
                brain.provider, "chat_completion", new_callable=AsyncMock
            ) as mock_chat:
                mock_chat.return_value = AsyncMock()  # Generic response

                await brain.adapt_tone(
                    excuse=AsyncMock(), risk=AsyncMock(), burnout=AsyncMock(), lang="ja"
                )

            # Check if the Japanese cultural prompt was used
            called_prompt = mock_chat.call_args[1]["messages"][0]["content"]
            assert "High-context Japanese tone" in called_prompt
            assert "harmony (wa)" in called_prompt


async def test_french_cultural_routing():
    from src.schemas.agents import CulturalPersona

    brain = CommitVigilBrain()
    mock_persona = CulturalPersona(
        code="fr",
        name="French",
        instruction="French Cartesian tone... eloquence...",
        is_verified=True,
    )

    with patch.object(brain, "detect_language", return_value="fr"):
        with patch.object(
            brain, "get_or_create_persona", new_callable=AsyncMock
        ) as mock_get_persona:
            mock_get_persona.return_value = mock_persona

            with patch.object(
                brain.provider, "chat_completion", new_callable=AsyncMock
            ) as mock_chat:
                mock_chat.return_value = AsyncMock()
                await brain.adapt_tone(
                    excuse=AsyncMock(), risk=AsyncMock(), burnout=AsyncMock(), lang="fr"
                )
            called_prompt = mock_chat.call_args[1]["messages"][0]["content"]
            assert "French Cartesian tone" in called_prompt
            assert "eloquence" in called_prompt


@pytest.mark.asyncio
async def test_british_english_detection_heuristic():
    """Verify that 'cheers mate' triggers en-UK even if standard en is detected."""
    brain = CommitVigilBrain()
    with patch.object(brain.provider, "chat_completion", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = LanguageResponse(code="en")  # Standard LLM result
        lang = await brain.detect_language("Cheers mate, I'll have it sorted.")
        assert lang == "en-UK"


@pytest.mark.asyncio
async def test_british_english_routing():
    """Verify that UK English triggers polite understatements."""
    from src.schemas.agents import CulturalPersona

    brain = CommitVigilBrain()
    mock_persona = CulturalPersona(
        code="en-UK",
        name="British",
        instruction="British professional tone... understatements...",
        is_verified=True,
    )

    # Explicitly asking for en-UK
    with patch.object(brain, "get_or_create_persona", new_callable=AsyncMock) as mock_get_persona:
        mock_get_persona.return_value = mock_persona

        with patch.object(brain.provider, "chat_completion", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = AsyncMock()
            await brain.adapt_tone(
                excuse=AsyncMock(), risk=AsyncMock(), burnout=AsyncMock(), lang="en-UK"
            )
        called_prompt = mock_chat.call_args[1]["messages"][0]["content"]
        assert "British professional tone" in called_prompt
        assert "understatements" in called_prompt


@pytest.mark.asyncio
async def test_spanish_cultural_routing():
    """Verify that Spanish triggers warm but boundaried persona."""
    from src.schemas.agents import CulturalPersona

    brain = CommitVigilBrain()
    mock_persona = CulturalPersona(
        code="es",
        name="Spanish",
        instruction="Spanish professional tone... Warm and engaging...",
        is_verified=True,
    )

    with patch.object(brain, "get_or_create_persona", new_callable=AsyncMock) as mock_get_persona:
        mock_get_persona.return_value = mock_persona

        with patch.object(brain.provider, "chat_completion", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = AsyncMock()
            await brain.adapt_tone(
                excuse=AsyncMock(), risk=AsyncMock(), burnout=AsyncMock(), lang="es"
            )
        called_prompt = mock_chat.call_args[1]["messages"][0]["content"]
        assert "Spanish professional tone" in called_prompt
        assert "Warm and engaging" in called_prompt


@pytest.mark.asyncio
async def test_finance_semantic_firewall():
    """Verify that Finance rules block market manipulation content."""
    supervisor = SafetySupervisor()
    with patch.object(supervisor.provider, "chat_completion", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = SafetyAudit(
            is_safe=False,
            is_hard_blocked=True,
            risk_of_morale_damage=0.3,
            supervisor_confidence=0.95,
            reasoning="Market manipulation alert",
            correction_type="none",
        )
        audit = await supervisor.audit_message(
            message="I'll pump the stock price if you finish this.",
            tone=ToneType.FIRM,
            user_context="finance_app",
            industry="finance",
        )
        assert audit.is_hard_blocked is True
        system_msg = mock_chat.call_args[1]["messages"][0]["content"]
        assert "Finance Ethics" in system_msg


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
            correction_type="none",
        )

        audit = await supervisor.audit_message(
            message="Please check the patient records for John Doe's treatment.",
            tone=ToneType.NEUTRAL,
            user_context="healthcare_app",
            industry="healthcare",
        )

        assert audit.is_hard_blocked is True
        assert "HIPAA" in audit.reasoning

        # Verify the system prompt was industry-specific
        system_msg = mock_chat.call_args[1]["messages"][0]["content"]
        assert "Healthcare Ethics" in system_msg


@pytest.mark.asyncio
async def test_feedback_loop_persistence():
    """Verify that manager feedback is actually persisted to the DB."""
    from sqlmodel import select

    from src.core.database import AsyncSessionLocal
    from src.schemas.agents import SafetyFeedback

    loop = SupervisorFeedbackLoop()

    await loop.log_manager_decision(
        intervention_id="int_123",
        user_id="dev_user",
        manager_id="mgr_456",
        action="accepted",
        message="Keep it up!",
        notes="Perfect correction.",
    )

    async with AsyncSessionLocal() as session:
        statement = select(SafetyFeedback).where(SafetyFeedback.intervention_id == "int_123")
        result = await session.execute(statement)
        feedback = result.scalar_one_or_none()

        assert feedback is not None
        assert feedback.action_taken == "accepted"
        assert feedback.manager_id == "mgr_456"
