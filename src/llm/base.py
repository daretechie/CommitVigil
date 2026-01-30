# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """
    Abstract Base Class for LLM Providers.
    Forces all providers to implement a structured completion method.
    """

    @property
    @abstractmethod
    def is_mock(self) -> bool:
        """Indicates if this is a mock provider."""
        pass

    @abstractmethod
    async def chat_completion(
        self, response_model: type[T], messages: list[dict[str, Any]], model: str
    ) -> T:
        pass
