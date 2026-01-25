from pydantic import BaseModel, Field
from src.llm.factory import LLMFactory
from src.schemas.performance import SlippageAnalysis
from src.core.logging import logger
from src.core.config import settings


class SlippageAnalyst:
    """
    The Specialized Intelligence Layer for GitOps Accountability.
    Analyzes 'Promise-vs-Reality' (Commit/PR) ratios.
    """

    def __init__(self, provider_name: str = None):
        self.provider = LLMFactory.get_provider(provider_name)
        self.model = settings.MODEL_NAME

    async def analyze_performance_gap(
        self, promised_tasks: list[str], actual_work_done: str
    ) -> SlippageAnalysis:
        """
        Calculates the slippage between what was committed in Git/Chat and what was delivered.
        """
        logger.info(
            "slippage_analysis_started",
            tasks_count=len(promised_tasks),
        )

        if self.provider.is_mock:
            from src.schemas.performance import SlippageStatus

            return SlippageAnalysis(
                status=SlippageStatus.ON_TRACK,
                fulfillment_ratio=0.9,
                detected_gap="Mock: High alignment detected.",
                risk_to_system_stability=0.1,
                intervention_required=False,
            )

        prompt = f"""
        Execute a high-stakes performance audit.
        
        PROMISED TASKS:
        {promised_tasks}
        
        ACTUAL WORK DONE (Evidence):
        {actual_work_done}
        
        Analyze if the developer is 'slipping' or creating 'shadow debt' (promising refactors but only doing hotfixes).
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


class TruthGapAnalysis(BaseModel):
    gap_detected: bool
    truth_score: float = Field(
        ..., ge=0, le=1, description="1.0 means perfect alignment."
    )
    explanation: str
    recommended_tone: str


class TruthGapDetector:
    """
    Correlation Layer: Compares verbal check-ins (Slack) vs technical reality (Git).
    """

    def __init__(self, provider_name: str = None):
        self.provider = LLMFactory.get_provider(provider_name)
        self.model = settings.MODEL_NAME

    async def detect_gap(
        self, check_in_text: str, technical_evidence: str
    ) -> TruthGapAnalysis:
        """
        Calculates the delta between what a human claims and what the code shows.
        """

        if self.provider.is_mock:
            return TruthGapAnalysis(
                gap_detected=False,
                truth_score=0.95,
                explanation="Mock: Claims match technical evidence.",
                recommended_tone="neutral",
            )

        prompt = f"""
        Human Claims (Slack): "{check_in_text}"
        Technical Evidence (Git Changes): {technical_evidence}
        
        Analyze the alignment. Is the user exaggerating progress? Are they being honest?
        Detect the 'Truth Gap'.
        """

        return await self.provider.chat_completion(
            response_model=TruthGapAnalysis,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Detect gaps between verbal claims and technical reality.",
                },
                {"role": "user", "content": prompt},
            ],
        )
