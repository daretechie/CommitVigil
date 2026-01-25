from src.core.config import settings
from src.llm.factory import LLMFactory
from src.schemas.agents import (
    ExcuseAnalysis,
    RiskAssessment,
    ExcuseCategory,
    RiskLevel,
    BurnoutDetection,
    ToneType,
    AgentDecision,
    ExtractedCommitment,
)


class CommitGuardBrain:
    """
    Elite Agent Brain: Decoupled from LLM Providers via LLMFactory.
    """

    def __init__(self):
        self.provider = LLMFactory.get_provider()
        self.model = settings.MODEL_NAME

    async def analyze_excuse(self, user_input: str) -> ExcuseAnalysis:
        # Behavioral Heuristics for Mock Mode
        if self.provider.is_mock:
            category = ExcuseCategory.DEFLECTION
            if any(
                word in user_input.lower() for word in ["sick", "hospital", "family"]
            ):
                category = ExcuseCategory.LEGITIMATE
            elif any(
                word in user_input.lower() for word in ["tired", "exhausted", "give up"]
            ):
                category = ExcuseCategory.BURNOUT_SIGNAL

            return ExcuseAnalysis(
                category=category,
                confidence_score=0.95,
                reasoning=f"Mock: Detected keywords in '{user_input}'",
            )

        return await self.provider.chat_completion(
            response_model=ExcuseAnalysis,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Analyze the user excuse for commitment failure.",
                },
                {"role": "user", "content": user_input},
            ],
        )

    async def assess_risk(
        self, historical_context: str, current_status: str
    ) -> RiskAssessment:
        if self.provider.is_mock:
            return RiskAssessment(
                risk_score=0.75,
                level=RiskLevel.HIGH,
                predicted_latency_days=3,
                mitigation_strategy="Mock: Suggest immediate PM intervention.",
            )

        return await self.provider.chat_completion(
            response_model=RiskAssessment,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Assess the risk of commitment failure based on history.",
                },
                {
                    "role": "user",
                    "content": f"History: {historical_context}\nStatus: {current_status}",
                },
            ],
        )

    async def detect_burnout(self, user_input: str) -> BurnoutDetection:
        if self.provider.is_mock:
            is_risk = any(
                word in user_input.lower()
                for word in ["exhausted", "cannot cope", "too much"]
            )
            return BurnoutDetection(
                is_at_risk=is_risk,
                sentiment_indicators=["high_fatigue"] if is_risk else [],
                recommendation="Suggest time off"
                if is_risk
                else "Continues monitoring",
            )

        return await self.provider.chat_completion(
            response_model=BurnoutDetection,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Detect signs of professional burnout in the user input.",
                },
                {"role": "user", "content": user_input},
            ],
        )

    async def extract_commitment(self, raw_input: str) -> ExtractedCommitment:
        if self.provider.is_mock:
            return ExtractedCommitment(
                task="Mock Task: " + raw_input[:20] + "...",
                deadline="Friday 5 PM",
                confidence_score=0.88,
            )

        return await self.provider.chat_completion(
            response_model=ExtractedCommitment,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Extract a task and deadline from the user's natural language promise.",
                },
                {"role": "user", "content": raw_input},
            ],
        )

    async def adapt_tone(
        self,
        excuse: ExcuseAnalysis,
        risk: RiskAssessment,
        burnout: BurnoutDetection,
        reliability_score: float = 100.0,
        consecutive_firm_calls: int = 0
    ) -> AgentDecision:
        if self.provider.is_mock:
            tone = ToneType.SUPPORTIVE
            
            # 1. THE BURNOUT SAFETY VALVE (Mandatory)
            if burnout.is_at_risk:
                tone = ToneType.SUPPORTIVE
                msg = f"I hear you. It sounds like you're reaching your limit. {burnout.recommendation}."
            
            # 2. TONE-DAMPING (Ethical Cooling-off)
            elif consecutive_firm_calls >= 3:
                tone = ToneType.NEUTRAL
                msg = "Let's reset and focus on a small, achievable win today. No pressure."
            
            # 3. RELIABILITY SCALING
            elif reliability_score < 50.0:
                tone = ToneType.CONFRONTATIONAL if reliability_score < 20 else ToneType.FIRM
                msg = "This is your third delay this month. We need an immediate recovery plan."
            
            # 4. DEFAULT
            else:
                msg = f"Thank you for the update. [Context: {settings.CULTURAL_DIRECTNESS_LEVEL} directness enabled]"

            return AgentDecision(
                action="none" if not (burnout.is_at_risk or reliability_score < 50) else "escalate_to_manager",
                tone=tone,
                message=msg,
                analysis_summary=f"Mock: Decision based on reliability of {reliability_score}% and {consecutive_firm_calls} firm calls."
            )

        # 5. ENTERPRISE LLM PROMPT (Self-Correction / Sensitivity)
        prompt = f"""
        Determine action and tone. 
        User Reliability: {reliability_score}%
        Consecutive Strict Interventions: {consecutive_firm_calls}
        Manager's Cultural Directness Setting: {settings.CULTURAL_DIRECTNESS_LEVEL}
        
        RULES:
        - If Consecutive Strict >= 3, you MUST use SUPPORTIVE/NEUTRAL tone to avoid morale burnout.
        - Respect the Cultural Directness: if 'low', soften all firm feedback.
        """

        return await self.provider.chat_completion(
            response_model=AgentDecision,
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Excuse: {excuse}\nRisk: {risk}\nBurnout: {burnout}"},
            ],
        )

