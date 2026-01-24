import pytest
from src.llm.factory import LLMFactory
from src.llm.openai import OpenAIProvider
from src.llm.groq import GroqProvider
from src.llm.mock import MockProvider
from src.core.config import settings

def test_llm_factory_mock():
    # Force mock mode by clearing keys
    settings.OPENAI_API_KEY = None
    settings.GROQ_API_KEY = None
    settings.LLM_PROVIDER = None
    
    provider = LLMFactory.get_provider()
    assert isinstance(provider, MockProvider)
    assert provider.is_mock is True

def test_llm_factory_openai_steering():
    settings.OPENAI_API_KEY = "dummy_key"
    settings.LLM_PROVIDER = "openai"
    
    provider = LLMFactory.get_provider()
    assert isinstance(provider, OpenAIProvider)

def test_llm_factory_groq_steering():
    settings.GROQ_API_KEY = "dummy_key"
    settings.LLM_PROVIDER = "groq"
    
    provider = LLMFactory.get_provider()
    assert isinstance(provider, GroqProvider)

@pytest.mark.asyncio
async def test_mock_provider_chat_completion():
    from src.schemas.agents import ExcuseAnalysis
    provider = MockProvider()
    response = await provider.chat_completion(
        response_model=ExcuseAnalysis,
        messages=[],
        model="any-model"
    )
    assert isinstance(response, ExcuseAnalysis)
