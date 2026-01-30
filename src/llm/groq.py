# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from typing import Any

import instructor
from groq import AsyncGroq
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.llm.base import LLMProvider, T


class GroqProvider(LLMProvider):
    client: Any | None

    def __init__(self, api_key: str):
        if api_key and api_key != "MOCK":
            self.client = instructor.from_groq(
                AsyncGroq(api_key=api_key), mode=instructor.Mode.JSON
            )
        else:
            # Handle the case where api_key is empty or "MOCK"
            # For now, we'll just set client to None or raise an error
            # depending on expected behavior. Assuming it should be handled
            # by the caller or a mock client should be assigned.
            # For this change, we'll assume a mock client is not explicitly
            # created here, and the system might rely on `is_mock` or
            # subsequent checks.
            self.client = None

    @property
    def is_mock(self) -> bool:
        return self.client is None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        reraise=True,
    )
    async def chat_completion(
        self, response_model: type[T], messages: list[dict[str, str]], model: str
    ) -> T:
        if not self.client:
            raise RuntimeError("Groq client not initialized. Provide a valid API Key.")

        # Default to a safe Llama 3 model if not specified or incompatible
        # (Though we pass the model from the Brain)
        return await self.client.chat.completions.create(
            model=model,
            response_model=response_model,
            messages=messages,  # type: ignore[arg-type]
        )
