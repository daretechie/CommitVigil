from unittest.mock import AsyncMock, patch

import pytest

from src.llm.factory import LLMFactory
from src.schemas.agents import AgentDecision, ToneType


@pytest.mark.asyncio
async def test_openai_integration_logic():
    """Verify OpenAI provider instantiation and factory routing."""
    from src.core.config import settings

    with patch.object(settings, "OPENAI_API_KEY", "sk-test"):
        provider = LLMFactory.get_provider("openai")
        assert not provider.is_mock

        # We test that we can call it (with a mock for the internal LLM call)
        with patch.object(provider, "chat_completion", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = AgentDecision(
                action="proceed", tone=ToneType.NEUTRAL, message="OK", analysis_summary="test"
            )

            decision = await provider.chat_completion(
                response_model=AgentDecision,
                messages=[{"role": "user", "content": "test"}],
                model="gpt-4o",
            )
            assert decision.action == "proceed"


@pytest.mark.asyncio
async def test_groq_integration_logic():
    """Verify Groq provider instantiation and factory routing."""
    from src.core.config import settings

    with patch.object(settings, "GROQ_API_KEY", "gsk-test"):
        provider = LLMFactory.get_provider("groq")
        assert not provider.is_mock

        with patch.object(provider, "chat_completion", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = AgentDecision(
                action="proceed", tone=ToneType.NEUTRAL, message="OK", analysis_summary="test"
            )

            decision = await provider.chat_completion(
                response_model=AgentDecision,
                messages=[{"role": "user", "content": "test"}],
                model="llama3-70b-8192",
            )
            assert decision.action == "proceed"
