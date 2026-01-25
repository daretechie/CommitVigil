import asyncio

from src.agents.safety import SafetySupervisor
from src.core.config import settings
from src.core.logging import logger
from src.llm.factory import LLMFactory
from src.schemas.agents import (
    AgentDecision,
    BurnoutDetection,
    ExcuseAnalysis,
    ExcuseCategory,
    ExtractedCommitment,
    PipelineEvaluation,
    RiskAssessment,
    RiskLevel,
    SafetyIntervention,
    ToneType,
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
                    "content": (
                        "Assess the risk of commitment failure based on history."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"History: {historical_context}\nStatus: {current_status}"
                    ),
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
                    "content": (
                        "Detect signs of professional burnout in the user input."
                    ),
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
                    "content": (
                        "Extract a task and deadline from the user's "
                        "natural language promise."
                    ),
                },
                {"role": "user", "content": raw_input},
            ],
        )

    async def evaluate_participation(
        self,
        user_id: str,
        commitment: str,
        check_in: str,
        reliability_score: float,
        consecutive_firm: int,
    ) -> PipelineEvaluation:
        """
        The Orchestration Pipeline: Decoupled and high-fidelity evaluation.
        """
        # 1. Parallel Analysis Phase (High Velocity)

        excuse_task = self.analyze_excuse(check_in)
        burnout_task = self.detect_burnout(check_in)
        risk_task = self.assess_risk(
            historical_context=str(reliability_score), current_status=check_in
        )

        excuse, burnout, risk = await asyncio.gather(
            excuse_task, burnout_task, risk_task
        )

        # 2. Decision Synthesis
        decision = await self.adapt_tone(
            excuse,
            risk,
            burnout,
            reliability_score=reliability_score,
            consecutive_firm_calls=consecutive_firm,
        )

        # 3. Final Ethical Supervision (Elite Guardrail)
        supervisor = SafetySupervisor()
        context = (
            f"User: {user_id}. Reliability: {reliability_score}%. "
            f"Consecutive firm: {consecutive_firm}."
        )

        audit = await supervisor.audit_message(decision.message, decision.tone, context)
        intervention = None

        # A. HARD BLOCK (HR Territory) - Immediate Escalation, No Retry
        if audit.is_hard_blocked:
            logger.critical(
                "hr_legal_boundary_detected", user_id=user_id, message=decision.message
            )
            decision.action = "escalate_to_manager"
            decision.message = (
                "This follow-up contains sensitive HR-related topics "
                "and has been blocked for manual manager review."
            )
            intervention = SafetyIntervention(
                original_message=decision.message,
                corrected_message=None,
                reasoning="HR/Legal Boundary Violation",
                intervention_type="block",
            )

        # B. SOFT CORRECTION (Tone/Cultural) - Injection Mechanism
        elif not audit.is_safe:
            logger.warning(
                "safety_correction_injected", user_id=user_id, reason=audit.reasoning
            )
            original = decision.message
            decision.message = audit.suggested_correction or decision.message
            decision.analysis_summary += f" | Safety Correction: {audit.reasoning}"
            intervention = SafetyIntervention(
                original_message=original,
                corrected_message=decision.message,
                reasoning=audit.reasoning,
                intervention_type="correction",
            )

        # C. AMBIGUITY (Low Confidence) - Human-in-the-Loop
        elif audit.requires_human_review:
            logger.info("human_review_requested", user_id=user_id)
            decision.action = "escalate_to_manager"
            decision.analysis_summary += " | Requires Human-in-the-Loop Review"
            intervention = SafetyIntervention(
                original_message=decision.message,
                corrected_message=None,
                reasoning="Confidence below threshold",
                intervention_type="review",
            )

        return PipelineEvaluation(
            decision=decision,
            excuse=excuse,
            risk=risk,
            burnout=burnout,
            safety_audit=intervention,
        )

    async def adapt_tone(
        self,
        excuse: ExcuseAnalysis,
        risk: RiskAssessment,
        burnout: BurnoutDetection,
        reliability_score: float = 100.0,
        consecutive_firm_calls: int = 0,
    ) -> AgentDecision:
        RELIABILITY_THRESHOLD = 50.0
        CRITICAL_THRESHOLD = 20.0
        CONSECUTIVE_LIMIT = 3

        if self.provider.is_mock:
            tone = ToneType.SUPPORTIVE

            # 1. THE BURNOUT SAFETY VALVE (Mandatory)
            if burnout.is_at_risk:
                tone = ToneType.SUPPORTIVE
                msg = (
                    f"I hear you. It sounds like you're reaching your limit. "
                    f"{burnout.recommendation}."
                )

            # 2. TONE-DAMPING (Ethical Cooling-off)
            elif consecutive_firm_calls >= CONSECUTIVE_LIMIT:
                tone = ToneType.NEUTRAL
                msg = (
                    "Let's reset and focus on a small, achievable win today. "
                    "No pressure."
                )

            # 3. RELIABILITY SCALING
            elif reliability_score < RELIABILITY_THRESHOLD:
                tone = (
                    ToneType.CONFRONTATIONAL
                    if reliability_score < CRITICAL_THRESHOLD
                    else ToneType.FIRM
                )
                msg = (
                    "This is your third delay this month. "
                    "We need an immediate recovery plan."
                )

            # 4. DEFAULT
            else:
                msg = (
                    f"Thank you for the update. [Context: "
                    f"{settings.CULTURAL_DIRECTNESS_LEVEL} directness enabled]"
                )

            return AgentDecision(
                action="none"
                if not (burnout.is_at_risk or reliability_score < RELIABILITY_THRESHOLD)
                else "escalate_to_manager",
                tone=tone,
                message=msg,
                analysis_summary=(
                    f"Mock: Decision based on reliability of {reliability_score}% "
                    f"and {consecutive_firm_calls} firm calls."
                ),
            )

        # 5. ENTERPRISE LLM PROMPT (Self-Correction / Sensitivity)
        prompt = f"""
        Determine action and tone.
        User Reliability: {reliability_score}%
        Consecutive Strict Interventions: {consecutive_firm_calls}
        Manager's Cultural Directness Setting: {settings.CULTURAL_DIRECTNESS_LEVEL}

        RULES:
        - If Consecutive Strict >= 3, you MUST use SUPPORTIVE/NEUTRAL tone
          to avoid morale burnout.
        - Respect the Cultural Directness: if 'low', soften all firm feedback.
        """

        return await self.provider.chat_completion(
            response_model=AgentDecision,
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"Excuse: {excuse}\nRisk: {risk}\nBurnout: {burnout}",
                },
            ],
        )
