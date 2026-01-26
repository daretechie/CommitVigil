from src.core.config import settings
from src.llm.factory import LLMFactory
from src.schemas.agents import SafetyAudit, ToneType


class SafetySupervisor:
    """
    The 'Overwatch' Layer: An autonomous agent that audits outgoing communications.
    This moves ethics from simple 'if/else' into sophisticated agentic reasoning.
    """

    def __init__(self, provider_name: str | None = None):
        self.provider = LLMFactory.get_provider(provider_name)
        self.model = settings.MODEL_NAME

    async def audit_message(
        self, message: str, tone: ToneType, user_context: str
    ) -> SafetyAudit:
        """
        Performs a final safety check on the proposed message.
        """

        prompt = f"""
        AUDIT REQUEST:
        
        CRITICAL TASKS:
        1. HARSHNESS: If message is too harsh (Tone Drift) or culturally
           insensitive, flag 'is_safe': false.
        2. HR BOUNDARIES (Hard Block):
           - Block Discussions on: Salary, Firing, PIPs, Legal Threats.
           - ALLOW Discussions on: Project Pricing, Budgeting, Cost Optimization.
           - If blocked, set 'is_hard_blocked': true.
        3. CORRECTION STRATEGY (Hybrid):
           - Minor Tone Issue -> Targeted phrase replacement. Set 'correction_type': 'surgical'.
           - Major Toxic Issue -> Full professional rewrite. Set 'correction_type': 'full_rewrite'.

        4. CONFIDENCE:
           - If unsure (e.g., ambiguous idioms), set 'supervisor_confidence' < {settings.SAFETY_CONFIDENCE_THRESHOLD}
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
                        "You are a specialized HR Ethics & Morale Safety Supervisor."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
