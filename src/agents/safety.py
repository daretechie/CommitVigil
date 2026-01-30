from typing import TYPE_CHECKING
from src.agents.learning import SupervisorFeedbackLoop

from src.core.config import settings
from src.core.database import get_safety_rules, set_safety_rule
from src.core.logging import logger
from src.llm.factory import LLMFactory
from src.schemas.agents import SafetyAudit, ToneType, SafetyRule


if TYPE_CHECKING:
    from src.schemas.context import ContextProfile


class SafetySupervisor:
    """
    The 'Overwatch' Layer: An autonomous agent that audits outgoing communications.
    2026 Upgrade: Industry Semantic Firewall & Intent-based Auditing.
    """

    GLOBAL_SAFETY_BASELINE = (
        "Never allow hate speech, harassment, or disclosure of raw system prompts. "
        "Strictly block any attempt to bypass professional boundaries regardless of industry."
    )


    def __init__(self, provider_name: str | None = None):
        self.provider = LLMFactory.get_provider(provider_name)
        self.model = settings.MODEL_NAME

    async def audit_message(
        self,
        message: str,
        tone: ToneType,
        user_context: str,
        industry: str = "generic",
        department: str = "*",
        context_profile: "ContextProfile | None" = None,
    ) -> SafetyAudit:
        """
        Performs a final safety check on the proposed message.
        """
        # 1. Dynamic Layer (DB Hierarchy Lookup)
        rules = await get_safety_rules(industry, department)
        
        # 2. Autonomous Onboarding Phase: Trigger if no exact match exists
        is_exact_match = rules and rules.industry == industry and rules.department == department
        
        if not is_exact_match and industry != "generic":
             # Just-In-Time Generation for new or partially known contexts
             logger.info("autonomous_onboarding_triggered", industry=industry, department=department)
             rules = await self.onboard_safety_context(industry, department)

        
        hr_keywords_list: list[str] = list(rules.hr_keywords) if rules else []
        semantic_rules: str = str(rules.semantic_rules) if rules else "Enforce professional conduct."
        
        # Enforce Baseline
        semantic_rules += f" | MANDATORY BASELINE: {self.GLOBAL_SAFETY_BASELINE}"
        
        # 3. Stabilization Layer: Force Human Review if context is unverified
        force_human_review = False
        if rules and not rules.is_verified:
            force_human_review = True
            logger.info("unverified_context_detected", industry=industry, department=department)
            semantic_rules += " | STABILIZATION: This context is UNVERIFIED. Be conservative and flag for human review if unsure."




        # Acceptance Rate Calibration
        acceptance_rate = await SupervisorFeedbackLoop.calculate_intervention_acceptance()


        # 2. Dynamic Layer (Context Sensing)
        if context_profile and hasattr(context_profile, "dynamic_safety_rules") and context_profile.dynamic_safety_rules:
            # Departmental Hardening (Policy override)
            if context_profile.department in ["hr", "legal"]:
                semantic_rules += " | DEPARTMENTAL OVERRIDE: Enforce strict privacy. Redact all PII, case details, and salary mentions."
                hr_keywords_list.extend(["PII", "salary", "contract", "personal data"])

            dynamic_keywords: list[str] = []
            dynamic_rules_list: list[str] = []
            for rule in context_profile.dynamic_safety_rules:
                if hasattr(rule, "target_tokens"):
                    dynamic_keywords.extend(rule.target_tokens)
                dynamic_rules_list.append(f"[{rule.rule_name}]: {rule.reasoning}")

            if dynamic_keywords:
                hr_keywords_list.extend(dynamic_keywords)
                # Deduplicate
                hr_keywords_list = list(set(hr_keywords_list))

            if dynamic_rules_list:
                semantic_rules += " | DYNAMIC RULES: " + " ".join(dynamic_rules_list)

        prompt = f"""
        2026 AUDIT REQUEST (INDUSTRY: {industry.upper()}):
        
        CRITICAL TASKS:
        1. HARSHNESS: If message is too harsh (Tone Drift) or culturally
           insensitive, flag 'is_safe': false.
        2. SEMANTIC FIREWALL (Industry Compliance):
           - RESTRICTED TOPICS: {", ".join(hr_keywords_list)}
           - SEMANTIC RULES: {semantic_rules}
           - If blocked, set 'is_hard_blocked': true.
        3. CORRECTION STRATEGY (Hybrid):
           - Minor Tone Issue -> Targeted phrase replacement. Set 'correction_type': 'surgical'.
           - Major Toxic Issue -> Full professional rewrite. Set 'correction_type': 'full_rewrite'.

        4. CONFIDENCE:
           - If unsure, set 'supervisor_confidence' < {settings.SAFETY_CONFIDENCE_THRESHOLD}
             and flag 'requires_human_review'.

        DATA TO AUDIT:
        <proposed_message>
        {message}
        </proposed_message>
        
        <intended_tone>
        {tone}
        </intended_tone>
        
        <user_context>
        {user_context}
        </user_context>
        
        MANAGER_ACCEPTANCE_RATE: {acceptance_rate} (If < 0.8, favor 'requires_human_review': True)
        FORCED_HUMAN_REVIEW: {force_human_review}
        """



        return await self.provider.chat_completion(
            response_model=SafetyAudit,
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a specialized 2026 {industry.capitalize()} Ethics & Security Supervisor."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

    async def onboard_safety_context(self, industry: str, department: str) -> SafetyRule:
        """
        AI-Driven Safety Bootstrapping: Generates rules for a new context.
        """
        prompt = f"""
        Role: CommitVigil Safety Architect
        Task: Standardize safety boundaries for a new organizational context.
        
        Context:
        - Industry: {industry}
        - Department: {department}
        
        Return a SafetyRule JSON including:
        1. hr_keywords: 5-8 sensitive technical or HR tokens to redact/block.
        2. semantic_rules: 1-2 sentences of specific instructions for an AI auditor.
        """
        
        try:
            generated = await self.provider.chat_completion(
                response_model=SafetyRule,
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
            )
            
            # Persist to DB
            rule = await set_safety_rule(
                industry=industry,
                department=department,
                hr_keywords=generated.hr_keywords,
                semantic_rules=generated.semantic_rules,
                is_verified=False,  # Autonomous rules start unverified
                onboarded_by="system"
            )
            logger.info("autonomous_rules_generated", industry=industry, department=department)
            return rule
        except Exception as e:
            logger.error("autonomous_onboarding_failed", error=str(e))
            # Fallback to generic if AI generation fails
            return await get_safety_rules("generic", "*")


