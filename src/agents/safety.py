from pydantic import BaseModel, Field

from src.core.config import settings
from src.llm.factory import LLMFactory
from src.schemas.agents import ToneType


class SafetyAudit(BaseModel):
    is_safe: bool
    requires_human_review: bool = False
    is_hard_blocked: bool = False  # For HR/Legal territory
    risk_of_morale_damage: float = Field(..., ge=0, le=1)
    supervisor_confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence in the audit verdict.",
    )
    suggested_correction: str | None = None
    correction_type: str = Field(
        default="none", description="'none', 'surgical', 'full_rewrite'"
    )
    reasoning: str



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
        if self.provider.is_mock:
            return SafetyAudit(
                is_safe=True,
                risk_of_morale_damage=0.05,
                supervisor_confidence=0.98,
                reasoning="Mock: Message appears professional and scoped correctly.",
            )

        prompt = f"""
        AUDIT REQUEST:
        Proposed Message: "{message}"
        Intended Tone: {tone}
        User Context (Reliability/History): {user_context}

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
           - If unsure (e.g., ambiguous idioms), set 'supervisor_confidence' < 0.8
             and flag 'requires_human_review'.
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
