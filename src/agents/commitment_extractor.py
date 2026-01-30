# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from src.core.config import settings
from src.core.utils import sanitize_prompt_input, truncate_text
from src.llm.factory import LLMFactory
from src.schemas.agents import SlackCommitmentRecord


class CommitmentExtractor:
    """
    Identity-Aware Commitment Extractor.
    Now leveraging the pluggable LLM Factory.
    """

    def __init__(self):
        self.provider = LLMFactory.get_provider()
        self.model = settings.MODEL_NAME

    async def parse_conversation(self, thread_text: str) -> SlackCommitmentRecord:
        """
        Extracts {who, what, when} from a raw conversation.
        Now includes 'Identity Attribution' logic.
        """
        sanitized_text = sanitize_prompt_input(truncate_text(thread_text, settings.MAX_INPUT_CHARS))
        return await self.provider.chat_completion(
            response_model=SlackCommitmentRecord,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract the primary promise from the conversation log provided within <conversation_log> tags. "
                        "Identify WHO made the promise. "
                        "If NO clear commitment or task is found, set 'commitment_found': False. "
                        "Otherwise, set 'commitment_found': True and fill fields. "
                        "Output: {commitment_found, who, what, when}."
                    ),
                },
                {
                    "role": "user",
                    "content": (f"<conversation_log>\n{sanitized_text}\n</conversation_log>"),
                },
            ],
        )
