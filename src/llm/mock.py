from enum import Enum
from typing import get_origin

from src.core.logging import logger
from src.llm.base import LLMProvider, T


class MockProvider(LLMProvider):
    """
    Elite Level Hermetic Mock Provider.
    Simulates LLM responses without external API calls.
    """

    @property
    def is_mock(self) -> bool:
        return True

    async def chat_completion(
        self, response_model: type[T], messages: list[dict[str, str]], model: str
    ) -> T:
        logger.warning("llm_mock_completion_triggered", provider="Mock", model=model)

        # Better Mocking: Try to find a way to instantiate the model with dummy data
        # Mapping model fields to dummy values
        dummy_data = {}
        for name, field in response_model.model_fields.items():
            annotation = field.annotation
            origin = get_origin(annotation)

            if annotation is str:
                dummy_data[name] = f"mock_{name}"
            elif annotation is float:
                dummy_data[name] = 0.95
            elif annotation is bool:
                dummy_data[name] = True
            elif annotation is int:
                dummy_data[name] = 1
            elif origin is list or (
                hasattr(annotation, "__name__") and annotation.__name__ == "list"
            ):
                dummy_data[name] = []
            elif isinstance(annotation, type) and issubclass(annotation, Enum):
                dummy_data[name] = next(iter(annotation))
            else:
                dummy_data[name] = None

        return response_model(**dummy_data)
