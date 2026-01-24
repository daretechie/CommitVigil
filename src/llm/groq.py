import instructor
from groq import AsyncGroq
from typing import Type
from src.llm.base import LLMProvider, T


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = instructor.patch(AsyncGroq(api_key=api_key))

    @property
    def is_mock(self) -> bool:
        return False

    async def chat_completion(
        self, response_model: Type[T], messages: list[dict[str, str]], model: str
    ) -> T:
        # Default to a safe Llama 3 model if not specified or incompatible
        # (Though we pass the model from the Brain)
        return await self.client.chat.completions.create(
            model=model, response_model=response_model, messages=messages
        )
