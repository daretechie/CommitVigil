import pytest
from unittest.mock import AsyncMock, patch
from src.schemas.agents import CulturalPersona
from src.agents.brain import CommitVigilBrain

@pytest.mark.asyncio
async def test_adaptive_persona_lookup_known():
    """
    Test that a known persona in the DB is returned correctly.
    """
    mock_persona = CulturalPersona(
        code="it",
        name="Italian",
        instruction="Italian Instruction",
        is_verified=True,
        source="system"
    )
    
    with patch("src.agents.brain.get_cultural_persona", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_persona
        
        brain = CommitVigilBrain()
        result = await brain.get_or_create_persona("it")
        
        assert result.code == "it"
        assert result.instruction == "Italian Instruction"
        mock_get.assert_called_once_with("it")

@pytest.mark.asyncio
async def test_adaptive_persona_drafting():
    """
    Test that an unknown persona triggers the autonomous drafting process.
    """
    with patch("src.agents.brain.get_cultural_persona", new_callable=AsyncMock) as mock_get, \
         patch("src.agents.brain.create_cultural_persona", new_callable=AsyncMock) as mock_create, \
         patch("src.llm.factory.LLMProvider.chat_completion", new_callable=AsyncMock) as mock_llm:
        
        # 1. Simulate DB Miss
        mock_get.return_value = None
        
        # 2. Simulate LLM Drafting Response
        mock_response = AsyncMock()
        mock_response.choices = [
            AsyncMock(message=AsyncMock(content="Auto Drafted Instruction"))
        ]
        mock_llm.return_value = mock_response
        
        # 3. Simulate DB Creation Return
        mock_create.side_effect = lambda p: p 
        
        brain = CommitVigilBrain()
        # Mock the provider on the instance to ensure our mock_llm is used
        brain.provider = AsyncMock()
        brain.provider.chat_completion = mock_llm
        brain.model = "gpt-4o"

        result = await brain.get_or_create_persona("nl")
        
        # Assertions
        assert result.code == "nl"
        assert result.instruction == "Auto Drafted Instruction"
        assert result.source == "auto_agent"
        assert result.is_verified is False
        
        mock_get.assert_called_with("nl")
        mock_llm.assert_called_once()
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_adapt_tone_uses_persona():
    """
    Test that adapt_tone injects the persona instruction into the prompt.
    """
    mock_persona = CulturalPersona(
        code="ja",
        name="Japanese",
        instruction="Strict Japanese Instruction",
        is_verified=True
    )
    
    with patch.object(CommitVigilBrain, "get_or_create_persona", new_callable=AsyncMock) as mock_get_persona, \
         patch("src.llm.factory.LLMProvider.chat_completion", new_callable=AsyncMock) as mock_chat:
        
        mock_get_persona.return_value = mock_persona
        
        brain = CommitVigilBrain()
        brain.provider = AsyncMock()
        brain.provider.chat_completion = mock_chat
        
        # Dummy inputs for adapt_tone
        from src.schemas.agents import ExcuseAnalysis, RiskAssessment, BurnoutDetection, ExcuseCategory, RiskLevel
        
        await brain.adapt_tone(
            excuse=ExcuseAnalysis(category=ExcuseCategory.LEGITIMATE, confidence_score=0.9, reasoning="Reasons"),
            risk=RiskAssessment(risk_score=0.1, level=RiskLevel.LOW, predicted_latency_days=0, mitigation_strategy="None"),
            burnout=BurnoutDetection(is_at_risk=False, sentiment_indicators=[], recommendation="None"),
            lang="ja"
        )
        
        kwargs = mock_chat.call_args.kwargs
        prompt_content = kwargs['messages'][0]['content'] # system message
        
        assert "Strict Japanese Instruction" in prompt_content
        assert "Respect the Cultural Persona above ALL else" in prompt_content
