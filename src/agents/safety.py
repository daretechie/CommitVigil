from src.core.config import settings
from src.llm.factory import LLMFactory
from src.schemas.agents import SafetyAudit, ToneType


class SafetySupervisor:
    """
    The 'Overwatch' Layer: An autonomous agent that audits outgoing communications.
    2026 Upgrade: Industry Semantic Firewall & Intent-based Auditing.
    """

    INDUSTRY_CONFIGS = {
        "healthcare": {
            "hr_keywords": ["HIPAA", "patient data", "medical records", "PHI", "PII"],
            "semantic_rules": "Redact any patient identifiers. Block messages mentioning medical charts or specific treatments.",
        },
        "finance": {
            "hr_keywords": [
                "insider trading",
                "SEC compliance",
                "FINRA",
                "market manipulation",
            ],
            "semantic_rules": "Block any phrasing that could be interpreted as financial advice or market manipulation.",
        },
        "generic": {
            "hr_keywords": ["Salary", "PIP", "Firing", "Legal Threats"],
            "semantic_rules": "Enforce standard professional conduct and HR boundaries.",
        },
    }

    def __init__(self, provider_name: str | None = None):
        self.provider = LLMFactory.get_provider(provider_name)
        self.model = settings.MODEL_NAME

    async def audit_message(
        self, message: str, tone: ToneType, user_context: str, industry: str = "generic"
    ) -> SafetyAudit:
        """
        Performs a final safety check on the proposed message.
        """
        config = self.INDUSTRY_CONFIGS.get(industry, self.INDUSTRY_CONFIGS["generic"])

        prompt = f"""
        2026 AUDIT REQUEST (INDUSTRY: {industry.upper()}):
        
        CRITICAL TASKS:
        1. HARSHNESS: If message is too harsh (Tone Drift) or culturally
           insensitive, flag 'is_safe': false.
        2. SEMANTIC FIREWALL (Industry Compliance):
           - RESTRICTED TOPICS: {", ".join(config["hr_keywords"])}
           - SEMANTIC RULES: {config["semantic_rules"]}
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
