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

        # Better Mocking: Try to find a way to instantiate the model with dummy data
        # Mapping model fields to dummy values
        dummy_data = {}
        for name, field in response_model.model_fields.items():
            if field.annotation == str:
                dummy_data[name] = f"mock_{name}"
            elif field.annotation == float:
                dummy_data[name] = 0.95
            elif field.annotation == bool:
                dummy_data[name] = True
            elif field.annotation == int:
                dummy_data[name] = 1
            elif hasattr(field.annotation, "__name__") and field.annotation.__name__ == "list":
                dummy_data[name] = []
            else:
                # For Enums or other complex types, we take the first value if it's an Enum
                from enum import Enum
                if isinstance(field.annotation, type) and issubclass(field.annotation, Enum):
                    dummy_data[name] = list(field.annotation)[0]
                else:
                    dummy_data[name] = None

        return response_model(**dummy_data)

