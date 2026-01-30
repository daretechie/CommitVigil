import asyncio

from src.agents.safety import SafetySupervisor
from src.agents.scout import ContextScout
from src.core.config import settings
from src.core.database import (
    create_cultural_persona,
    get_cultural_persona,
    get_user_history,
)
from src.core.logging import logger
from src.core.monitoring import LatencyMonitor
from src.core.persona import CULTURAL_PROMPTS
from src.core.utils import sanitize_prompt_input
from src.llm.factory import LLMFactory
from src.schemas.agents import (
    AgentDecision,
    BurnoutDetection,
    CulturalPersona,
    ExcuseAnalysis,
    ExcuseCategory,
    LanguageResponse,
    PipelineEvaluation,
    RiskAssessment,
    RiskLevel,
    SafetyIntervention,
    ToneType,
)
from src.schemas.context import ContextProfile


class CommitVigilBrain:
    """
    Elite Agent Brain: Decoupled from LLM Providers via LLMFactory.
    2026 Upgrade: Cultural Persona Routing & Industry Intelligence.
    """

    def __init__(self):
        self.provider = LLMFactory.get_provider()
        self.scout = ContextScout()
        self.supervisor = SafetySupervisor()
        self.model = settings.MODEL_NAME

    async def detect_language(self, text: str) -> str:
        """
        2026 Agentic Language & Culture Detection.
        Identifies the primary language and mapping it to our cultural archetypes.
        """
        if not text:
            return "en"

        try:
            detected = await self.provider.chat_completion(
                response_model=LanguageResponse,
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Detect the language of the following text. Return a JSON with a single field 'code' containing the 2-letter ISO code (e.g., 'en', 'ja', 'de', 'fr', 'es').",
                    },
                    {"role": "user", "content": text},
                ],
            )
            # Normalize and map to supported types
            code = detected.code.strip().lower()

            # Handle regional variations for English
            if code == "en":
                from src.core.constants import UK_ENGLISH_KEYWORDS

                text_lower = text.lower()
                if any(word in text_lower for word in UK_ENGLISH_KEYWORDS):
                    return "en-UK"

            return code if code in CULTURAL_PROMPTS else "en"
        except Exception:
            logger.exception("language_detection_failed")
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
                    "content": f"<user_excuse>\n{sanitize_prompt_input(user_input)}\n</user_excuse>",
                },
            ],
        )

    async def assess_risk(self, historical_context: str, current_status: str) -> RiskAssessment:
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
                        f"<historical_context>\n{sanitize_prompt_input(historical_context)}\n</historical_context>\n"
                        f"<current_status>\n{sanitize_prompt_input(current_status)}\n</current_status>"
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
                    "content": f"<user_input>\n{sanitize_prompt_input(user_input)}\n</user_input>",
                },
            ],
        )

    async def _get_context_profile(
        self, user_id: str, check_in: str, industry: str | None
    ) -> tuple[ContextProfile, str, str]:
        """Helper to resolve industry/department context."""
        user_history = await get_user_history(user_id)
        if user_history and user_history.is_context_verified:
            target_industry = user_history.industry_type
            target_department = user_history.department
            logger.info(
                "context_lock_active",
                user_id=user_id,
                industry=target_industry,
                department=target_department,
            )
            return (
                ContextProfile(
                    industry=target_industry,
                    department=target_department,
                    confidence=1.0,
                    reasoning="Manually verified context (Locked).",
                ),
                target_industry,
                target_department,
            )

        if industry == "AUTO":
            profile = await self.scout.sense_context([check_in])
            target_industry = str(profile.industry)
            target_department = str(profile.department)
            logger.info(
                "dynamic_context_sensing", industry=target_industry, department=target_department
            )
            return profile, target_industry, target_department

        target_industry = str(industry or settings.SELECTED_INDUSTRY)
        target_department = "*"
        return (
            ContextProfile(
                industry=target_industry,
                department=target_department,
                confidence=1.0,
                reasoning="Static context provided",
            ),
            target_industry,
            target_department,
        )

    async def _run_parallel_analysis(
        self, check_in: str, reliability_score: float, lang: str | None
    ) -> tuple[ExcuseAnalysis, BurnoutDetection, RiskAssessment, str]:
        """Helper to orchestrate parallel LLM calls."""
        tasks = [
            self.analyze_excuse(check_in),
            self.detect_burnout(check_in),
            self.assess_risk(
                historical_context=str(reliability_score),
                current_status=check_in,
            ),
        ]
        if not lang:
            tasks.append(self.detect_language(check_in))

        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=60.0)
        target_lang = lang if lang else results[3]
        return results[0], results[1], results[2], target_lang

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
        context_profile, target_industry, target_department = await self._get_context_profile(
            user_id, check_in, industry
        )

        try:
            excuse, burnout, risk, target_lang = await self._run_parallel_analysis(
                check_in, reliability_score, lang
            )
        except TimeoutError:
            logger.error("orchestration_timeout", user_id=user_id, status="aborting_pipeline")
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
                context_profile=context_profile,
            )

        # 3. Final Ethical Supervision (Semantic Firewall)
        context = (
            f"User: {user_id}. Reliability: {reliability_score}%. "
            f"Consecutive firm: {consecutive_firm}. Industry: {target_industry}."
        )

        with LatencyMonitor("safety_supervisor_latency", user_id):
            audit = await self.supervisor.audit_message(
                decision.message,
                decision.tone,
                context,
                industry=target_industry,
                department=target_department,
                context_profile=context_profile,
            )

        intervention = None

        if audit.is_hard_blocked:
            logger.critical("hr_legal_boundary_detected", user_id=user_id, message=decision.message)
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
            logger.warning("safety_correction_injected", user_id=user_id, reason=audit.reasoning)
            original = decision.message
            raw_correction = audit.suggested_correction or decision.message
            if raw_correction and len(raw_correction) > 0:
                raw_correction = raw_correction[0].upper() + raw_correction[1:]

            decision.message = raw_correction
            decision.analysis_summary += f" | Safety Correction: {audit.reasoning}"

            re_audit = await self.supervisor.audit_message(
                decision.message,
                decision.tone,
                context,
                industry=target_industry,
                department=target_department,
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

    async def get_or_create_persona(self, lang: str) -> CulturalPersona:
        """
        Adaptive Learning: Fetch known persona or autonomously draft a new one.
        """
        lang = lang.lower()
        persona = await get_cultural_persona(lang)

        if not persona:
            # Check if we need to seed defaults first?
            # Actually, let's try to draft it if it's missing entirely.
            if lang == "en":  # Fallback if DB is empty and cache missed
                return CulturalPersona(
                    code="en",
                    name="Standard English",
                    instruction="Standard global professional tone. Clear and direct.",
                    is_verified=True,
                    source="system_fallback",
                )

            logger.info("unknown_culture_detected", lang=lang, action="autonomously_drafting")
            persona = await self.draft_new_persona(lang)

        return persona

    async def draft_new_persona(self, lang: str) -> CulturalPersona:
        """
        Agentic Workflow: Ask the LLM to define the professional communication style for this culture.
        """
        try:
            # We ask the model to generate the instruction
            prompt = f"""
            You are an expert Cultural Anthropologist and Business Communication Specialist.

            Task: Define the 'Professional Communication Style' for the language/region code: '{lang}'.
            Focus on:
            - Directness vs. Indirectness
            - Hierarchy and Humility (Power Distance)
            - Relationship vs. Task orientation
            - Key cultural values (e.g., 'Wa' in Japan, 'Guanxi' in China)

            Output: A single, concise paragraph (max 40 words) that instructs an AI agent how to mime this persona.
            Start with: "{lang.upper()} professional tone. ..."
            """

            response = await self.provider.chat_completion(
                response_model=None,  # Raw string response
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )

            instruction = response.choices[0].message.content.strip()

            new_persona = CulturalPersona(
                code=lang,
                name=f"Adaptive {lang.upper()} Persona",
                instruction=instruction,
                is_verified=False,  # Requires HITL approval
                source="auto_agent",
            )

            return await create_cultural_persona(new_persona)

        except Exception as e:
            logger.error("persona_drafting_failed", lang=lang, error=str(e))
            # Fallback to English
            return CulturalPersona(
                code=lang,
                name=f"Fallback {lang}",
                instruction="Standard professional tone. Be clear and polite.",
                is_verified=True,
                source="fallback",
            )

    async def adapt_tone(
        self,
        excuse: ExcuseAnalysis,
        risk: RiskAssessment,
        burnout: BurnoutDetection,
        reliability_score: float = 100.0,
        consecutive_firm_calls: int = 0,
        lang: str = "en",
        context_profile: ContextProfile | None = None,
    ) -> AgentDecision:
        # Dynamic Persona Lookup
        persona = await self.get_or_create_persona(lang)
        cultural_instruction = persona.instruction

        # If unverified, maybe append a warning or safe-mode instruction?
        if not persona.is_verified:
            cultural_instruction += " (Maintain extreme strictness on professional boundaries as this persona is unverified)."

        industry = context_profile.industry if context_profile else "generic"
        formality = context_profile.formality if context_profile else "informal"
        culture_profile = context_profile.culture if context_profile else "low_context"

        prompt = f"""
        Role: CommitVigil Decision Agent
        Focus Industry: {industry}
        Organizational Formality: {formality}
        Cultural Profile: {culture_profile}
        Cultural Persona Instruction: {cultural_instruction}

        Context:
        - User Reliability: {reliability_score}%
        - Consecutive Strict Interventions: {consecutive_firm_calls}
        - Cultural Directness: {settings.CULTURAL_DIRECTNESS_LEVEL}

        Rules:
        - If Consecutive Strict >= 3, use SUPPORTIVE/NEUTRAL tone.
        - Respect the Cultural Persona above ALL else.
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
