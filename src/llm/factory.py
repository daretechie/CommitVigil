from src.core.config import settings
from src.core.logging import logger
from src.llm.base import LLMProvider
from src.llm.openai import OpenAIProvider
from src.llm.groq import GroqProvider
from src.llm.mock import MockProvider


class LLMFactory:
    """
    Elite LLM Factory with Automatic Key Detection.
    """

    @staticmethod
    def get_provider() -> LLMProvider:
        # 1. Respect explicit steering if set
        if settings.LLM_PROVIDER:
            if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
                return OpenAIProvider(api_key=settings.OPENAI_API_KEY)
            if settings.LLM_PROVIDER == "groq" and settings.GROQ_API_KEY:
                return GroqProvider(api_key=settings.GROQ_API_KEY)
            if settings.LLM_PROVIDER == "mock":
                return MockProvider()

        # 2. Automatic Detection (Heuristic Discovery)
        if settings.OPENAI_API_KEY:
            logger.info("llm_factory_auto_detect", provider="OpenAI")
            return OpenAIProvider(api_key=settings.OPENAI_API_KEY)

        if settings.GROQ_API_KEY:
            logger.info("llm_factory_auto_detect", provider="Groq")
            return GroqProvider(api_key=settings.GROQ_API_KEY)

        # 3. Fallback to Hermetic Mock
        logger.warning("llm_factory_fallback", reason="NO_KEYS_AVAILABLE", mode="MOCK")
        return MockProvider()
