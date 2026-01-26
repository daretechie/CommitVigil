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
    2026 Upgrade: Cultural Persona Routing & Industry Intelligence.
    """

    CULTURAL_PROMPTS = {
        "en": "Standard global professional tone. Clear and direct.",
        "en-UK": "British professional tone. Use polite understatements, 'please/thank you' frequency, and avoid over-assertiveness.",
        "ja": "High-context Japanese tone. Prioritize harmony (wa). Use indirect observations and soft suggestions instead of direct demands.",
        "de": "Direct German Sachlichkeit. Focus on objective facts, precision, and substantive feedback.",
        "fr": "French professional tone. Value eloquence and formal structure. Maintain a balance between directness and professional courtesy.",
        "es": "Spanish professional tone. Warm and engaging but maintain professional boundaries. Value personal connection while enforcing deadlines.",
    }

    def __init__(self):
        self.provider = LLMFactory.get_provider()
        self.model = settings.MODEL_NAME

    async def detect_language(self, text: str) -> str:
        """
        2026 Agentic Language & Culture Detection.
        Identifies the primary language and mapping it to our cultural archetypes.
        """
        try:
            detected = await self.provider.chat_completion(
                response_model=str,
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Detect the language of the following text. Return only the 2-letter ISO code (e.g., 'en', 'ja', 'de', 'fr', 'es').",
                    },
                    {"role": "user", "content": text},
                ],
            )
            # Normalize and map to supported types
            code = str(detected).strip().lower()
            return code if code in self.CULTURAL_PROMPTS else "en"
        except Exception:
            return "en"

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
        lang: str | None = None,
        industry: str | None = None,
    ) -> PipelineEvaluation:
        """
        The Orchestration Pipeline: Decoupled and high-fidelity evaluation.
        """
        # 0. Language Awareness
        target_lang = lang or await self.detect_language(check_in)
        target_industry = industry or settings.SELECTED_INDUSTRY

        try:
            # 1. Parallel Analysis Phase (High Velocity) with Safety Timeout
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
            return PipelineEvaluation(
                decision=AgentDecision(
                    action="escalate_to_manager",
                    tone=ToneType.NEUTRAL,
                    message="I'm experiencing a delay in analysis. Please maintain your commitments.",
                    analysis_summary="Orchestration Timeout: AI Providers failed to respond within 30s.",
                ),
                excuse=ExcuseAnalysis(
                    category=ExcuseCategory.LEGITIMATE,
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

        # 2. Decision Synthesis (Culture & Industry Aware)
        with LatencyMonitor("decision_synthesis_latency", user_id):
            decision = await self.adapt_tone(
                excuse,
                risk,
                burnout,
                reliability_score=reliability_score,
                consecutive_firm_calls=consecutive_firm,
                lang=target_lang,
                industry=target_industry,
            )

        # 3. Final Ethical Supervision (Semantic Firewall)
        supervisor = SafetySupervisor()
        context = (
            f"User: {user_id}. Reliability: {reliability_score}%. "
            f"Consecutive firm: {consecutive_firm}. Industry: {target_industry}."
        )

        with LatencyMonitor("safety_supervisor_latency", user_id):
            audit = await supervisor.audit_message(
                decision.message, decision.tone, context, industry=target_industry
            )

        intervention = None

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

        elif not audit.is_safe:
            logger.warning(
                "safety_correction_injected", user_id=user_id, reason=audit.reasoning
            )
            original = decision.message
            raw_correction = audit.suggested_correction or decision.message
            if raw_correction and len(raw_correction) > 0:
                raw_correction = raw_correction[0].upper() + raw_correction[1:]

            decision.message = raw_correction
            decision.analysis_summary += f" | Safety Correction: {audit.reasoning}"

            re_audit = await supervisor.audit_message(
                decision.message, decision.tone, context, industry=target_industry
            )
            if not re_audit.is_safe:
                logger.critical(
                    "unsafe_correction_caught",
                    user_id=user_id,
                    bad_fix=decision.message,
                )
                decision.action = "escalate_to_manager"
                decision.message = (
                    "Automated correction failed safety check. Manual review required."
                )
                intervention = SafetyIntervention(
                    original_message=original,
                    corrected_message=None,
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
        lang: str = "en",
        industry: str = "generic",
    ) -> AgentDecision:
        # 2026 Cultural Persona Logic
        cultural_instruction = self.CULTURAL_PROMPTS.get(
            lang, self.CULTURAL_PROMPTS["en"]
        )

        prompt = f"""
        Role: CommitGuard Decision Agent
        Focus Industry: {industry}
        Cultural Persona: {cultural_instruction}

        Context:
        - User Reliability: {reliability_score}%
        - Consecutive Strict Interventions: {consecutive_firm_calls}
        - Cultural Directness: {settings.CULTURAL_DIRECTNESS_LEVEL}

        Rules:
        - If Consecutive Strict >= 3, use SUPPORTIVE/NEUTRAL tone.
        - Respect the Cultural Persona above above ALL else. 
        - If industry is 'healthcare' or 'finance', avoid any phrasing that implies legally binding commitments unless explicit.
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
