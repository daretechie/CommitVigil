import asyncio

from src.agents.safety import SafetySupervisor
from src.core.config import settings
from src.core.logging import logger
from src.core.monitoring import LatencyMonitor
from src.llm.factory import LLMFactory


from src.schemas.agents import (
    AgentDecision,
    BurnoutDetection,
    ExcuseAnalysis,
    ExcuseCategory,
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
        return await self.provider.chat_completion(
            response_model=ExcuseAnalysis,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Analyze the user excuse for commitment failure provided within <user_excuse> tags.",
                },
                {
                    "role": "user",
                    "content": f"<user_excuse>\n{user_input}\n</user_excuse>",
                },
            ],
        )

    async def assess_risk(
        self, historical_context: str, current_status: str
    ) -> RiskAssessment:
        return await self.provider.chat_completion(
            response_model=RiskAssessment,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Assess the risk of commitment failure based on the provided "
                        "history and current status within their respective XML tags."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"<historical_context>\n{historical_context}\n</historical_context>\n"
                        f"<current_status>\n{current_status}\n</current_status>"
                    ),
                },
            ],
        )

    async def detect_burnout(self, user_input: str) -> BurnoutDetection:
        return await self.provider.chat_completion(
            response_model=BurnoutDetection,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Detect signs of professional burnout in the user input provided within <user_input> tags."
                    ),
                },
                {
                    "role": "user",
                    "content": f"<user_input>\n{user_input}\n</user_input>",
                },
            ],
        )

    async def evaluate_participation(
        self,
        user_id: str,
        check_in: str,
        reliability_score: float,
        consecutive_firm: int,
    ) -> PipelineEvaluation:
        """
        The Orchestration Pipeline: Decoupled and high-fidelity evaluation.
        """
        try:
            # 1. Parallel Analysis Phase (High Velocity) with Safety Timeout
            # We enforce a 30s SLA for the initial heuristic/LLM sweep.
            excuse, burnout, risk = await asyncio.wait_for(
                asyncio.gather(
                    self.analyze_excuse(check_in),
                    self.detect_burnout(check_in),
                    self.assess_risk(
                        historical_context=str(reliability_score),
                        current_status=check_in,
                    ),
                ),
                timeout=30.0,
            )
        except asyncio.TimeoutError:
            logger.error(
                "orchestration_timeout", user_id=user_id, status="aborting_pipeline"
            )
            # Fallback for critical failure: supportive neutral message
            return PipelineEvaluation(
                decision=AgentDecision(
                    action="escalate_to_manager",
                    tone=ToneType.NEUTRAL,
                    message="I'm experiencing a delay in analysis. Please maintain your commitments.",
                    analysis_summary="Orchestration Timeout: AI Providers failed to respond within 30s.",
                ),
                excuse=ExcuseAnalysis(
                    category=ExcuseCategory.LEGITIMATE,  # Benefit of the doubt
                    confidence_score=0.0,
                    reasoning="Timeout: Analysis incomplete.",
                ),
                risk=RiskAssessment(
                    risk_score=0.0,
                    level=RiskLevel.LOW,
                    predicted_latency_days=0,
                    mitigation_strategy="None (Timeout)",
                ),
                burnout=BurnoutDetection(
                    is_at_risk=False,
                    sentiment_indicators=[],
                    recommendation="Monitor manually (System Timeout)",
                ),
            )

        # 2. Decision Synthesis
        with LatencyMonitor("decision_synthesis_latency", user_id):
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

        with LatencyMonitor("safety_supervisor_latency", user_id):
            audit = await supervisor.audit_message(
                decision.message, decision.tone, context
            )

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
            # Capitalization Hook: Ensure correction starts with uppercase
            raw_correction = audit.suggested_correction or decision.message
            if raw_correction and len(raw_correction) > 0:
                raw_correction = raw_correction[0].upper() + raw_correction[1:]

            decision.message = raw_correction
            decision.analysis_summary += f" | Safety Correction: {audit.reasoning}"

            # --- SAFETY VALVE: RE-VALIDATION (Tier 4 Humility) ---
            # Verify the correction itself is not unsafe (e.g., hallucinated threat).
            # This doubles latency but ensures zero-trust safety.
            re_audit = await supervisor.audit_message(
                decision.message, decision.tone, context
            )
            if not re_audit.is_safe:
                logger.critical(
                    "unsafe_correction_caught",
                    user_id=user_id,
                    bad_fix=decision.message,
                )
                # Fallback to HITL if the AI failed to fix it safely
                decision.action = "escalate_to_manager"
                decision.message = (
                    "Automated correction failed safety check. Manual review required."
                )
                intervention = SafetyIntervention(
                    original_message=original,
                    corrected_message=None,  # Discard unsafe fix
                    reasoning="Safety Valve Triggered: Correction was still unsafe.",
                    intervention_type="review",
                )
            else:
                intervention = SafetyIntervention(
                    original_message=original,
                    corrected_message=decision.message,
                    reasoning=audit.reasoning,
                    intervention_type="correction",
                )

        # C. AMBIGUITY (Low Confidence) - Human-in-the-Loop
        elif (
            audit.requires_human_review
            or audit.supervisor_confidence < settings.SAFETY_CONFIDENCE_THRESHOLD
        ):
            logger.info("human_review_requested", user_id=user_id)
            decision.action = "escalate_to_manager"
            decision.analysis_summary += " | Requires Human-in-the-Loop Review"
            intervention = SafetyIntervention(
                original_message=decision.message,
                corrected_message=None,
                reasoning=f"Confidence below threshold ({audit.supervisor_confidence})",
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
        # ENTERPRISE LLM PROMPT (Self-Correction / Sensitivity)
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
