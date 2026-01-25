import instructor
from openai import AsyncOpenAI

from src.llm.base import LLMProvider, T


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = instructor.patch(AsyncOpenAI(api_key=api_key))

    @property
    def is_mock(self) -> bool:
        return False

    async def chat_completion(
        self, response_model: type[T], messages: list[dict[str, str]], model: str
    ) -> T:
        return await self.client.chat.completions.create(
            model=model, response_model=response_model, messages=messages
        )
