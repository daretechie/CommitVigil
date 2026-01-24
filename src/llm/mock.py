from typing import Type
from src.llm.base import LLMProvider, T
from src.core.logging import logger


class MockProvider(LLMProvider):
    """
    Elite Level Hermetic Mock Provider.
    Simulates LLM responses without external API calls.
    """

    @property
    def is_mock(self) -> bool:
        return True

    async def chat_completion(
        self, response_model: Type[T], messages: list[dict[str, str]], model: str
    ) -> T:
        logger.warning("llm_mock_completion_triggered", provider="Mock", model=model)

        # Logic to return a generic instance of the response_model
        # In a real elite system, you'd use factory_boy or similar
        # For now, we rely on the Pydantic model's ability to be instantiated with dummy data
        return response_model.model_construct()
