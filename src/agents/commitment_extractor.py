from src.core.config import settings
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
        if self.provider.is_mock:
            # Elite Identity Attribution Mock
            # If the text mentions a name or 'I am X', we attribute it.
            who = "John"
            if "I am" in thread_text:
                who = thread_text.split("I am")[1].split()[0].strip(",. ")
            elif "promised" in thread_text:
                parts = thread_text.split()
                if parts:
                    who = parts[0]  # Assume the first word for mock

            return SlackCommitmentRecord(who=who, what="Fix API bug", when="Friday")

        return await self.provider.chat_completion(
            response_model=SlackCommitmentRecord,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Extract the primary promise. Identify WHO made the promise. Output: {who, what, when}.",
                },
                {"role": "user", "content": thread_text},
            ],
        )
