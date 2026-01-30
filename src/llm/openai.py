# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from typing import Any, cast

import instructor
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.llm.base import LLMProvider, T


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = instructor.from_openai(AsyncOpenAI(api_key=api_key))

    @property
    def is_mock(self) -> bool:
        return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        reraise=True,
    )
    async def chat_completion(
        self, response_model: type[T], messages: list[dict[str, Any]], model: str
    ) -> T:
        return await self.client.chat.completions.create(
            model=model, response_model=response_model, messages=cast(Any, messages)
        )
