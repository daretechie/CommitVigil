
from src.core.config import settings
from src.core.logging import logger
from src.core.utils import truncate_text
from src.llm.factory import LLMFactory
from src.schemas.performance import SlippageAnalysis, TruthGapAnalysis


class SlippageAnalyst:
    """
    The Specialized Intelligence Layer for GitOps Accountability.
    Analyzes 'Promise-vs-Reality' (Commit/PR) ratios.
    """

    def __init__(self, provider_name: str | None = None):
        self.provider = LLMFactory.get_provider(provider_name)
        self.model = settings.MODEL_NAME

    async def analyze_performance_gap(
        self, promised_tasks: list[str], actual_work_done: str
    ) -> SlippageAnalysis:
        """
        Calculates the slippage between what was committed in Git/Chat
        and what was delivered.
        """
        logger.info(
            "slippage_analysis_started",
            tasks_count=len(promised_tasks),
        )

        prompt = f"""
        Execute a high-stakes performance audit.

        PROMISED TASKS:
        {truncate_text(str(promised_tasks), settings.MAX_INPUT_CHARS // 2)}

        ACTUAL WORK DONE (Evidence):
        {truncate_text(actual_work_done, settings.MAX_INPUT_CHARS)}


        Analyze if the developer is 'slipping' or creating 'shadow debt'
        (promising refactors but only doing hotfixes).
        """

        return await self.provider.chat_completion(
            response_model=SlippageAnalysis,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a specialized performance auditor.",
                },
                {"role": "user", "content": prompt},
            ],
        )




class TruthGapDetector:
    """
    Correlation Layer: Compares verbal check-ins (Slack) vs technical reality (Git).
    """

    def __init__(self, provider_name: str | None = None):
        self.provider = LLMFactory.get_provider(provider_name)
        self.model = settings.MODEL_NAME

    async def detect_gap(
        self, check_in_text: str, technical_evidence: str
    ) -> TruthGapAnalysis:
        """
        Calculates the delta between what a human claims and what the code shows.
        """

        prompt = f"""
        Human Claims (Slack): "{truncate_text(check_in_text, settings.MAX_INPUT_CHARS // 2)}"
        Technical Evidence (Git Changes): {truncate_text(technical_evidence, settings.MAX_INPUT_CHARS)}


        Analyze the alignment. Is the user exaggerating progress? Are they being honest?
        Detect the 'Truth Gap'.
        """

        return await self.provider.chat_completion(
            response_model=TruthGapAnalysis,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Detect gaps between verbal claims and technical reality."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
