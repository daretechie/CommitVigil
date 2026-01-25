from src.llm.factory import LLMFactory
from src.schemas.performance import SlippageAnalysis, SlippageStatus
from src.core.logging import logger


class SlippageAnalyst:
    """
    The Specialized Intelligence Layer for GitOps Accountability.
    Analyzes 'Promise-vs-Reality' (Commit/PR) ratios.
    """

    def __init__(self, provider_name: str = None):
        self.llm = LLMFactory.get_provider(provider_name)

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

        prompt = f"""
        Execute a high-stakes performance audit.
        
        PROMISED TASKS:
        {promised_tasks}
        
        ACTUAL WORK DONE (Evidence):
        {actual_work_done}
        
        Analyze if the developer is 'slipping' or creating 'shadow debt' (promising refactors but only doing hotfixes).
        """

        analysis: SlippageAnalysis = await self.llm.generate(
            prompt=prompt, response_model=SlippageAnalysis
        )

        logger.info(
            "slippage_analysis_complete",
            status=analysis.status,
            ratio=analysis.fulfillment_ratio,
        )

        return analysis
