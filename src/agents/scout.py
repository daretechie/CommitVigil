# Copyright (c) 2026 CommitVigil AI. All rights reserved.

from src.core.config import settings
from src.core.logging import logger
from src.llm.factory import LLMFactory
from src.schemas.context import (
    ContextProfile,
    CulturalContext,
    FormalityLevel,
    IndustryType,
)


class ContextScout:
    """
    Forensic Context Scout Agent: Automatically senses the domain and culture.
    Uses Zero-Shot Domain Detection to adapt the forensic engine.
    """

    def __init__(self):
        self.provider = LLMFactory.get_provider()
        self.model = settings.MODEL_NAME

    async def sense_context(self, text_samples: list[str]) -> ContextProfile:
        """
        Senses the industry, department, culture, and organizational norms.
        """
        import re

        # Basic PII Scrubbing (Privacy-preserving sensing)
        scrubbed_samples = []
        for text in text_samples[:10]:
            # Redact emails
            text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "[EMAIL]", text)
            # Redact common name-like patterns or specific Slack IDs
            text = re.sub(r"<@U[A-Z0-9]+>", "[SLACK_ID]", text)
            scrubbed_samples.append(text)

        combined_text = "\n---\n".join(scrubbed_samples)

        prompt = f"""
        Role: CommitVigil Forensic Context Scout
        Task: Analyze the communication samples below and determine the organizational and departmental profile.

        Samples:
        {combined_text}

        Return a ContextProfile JSON including:
        1. industry: The industry name (e.g., 'aerospace', 'biotech', 'gaming'). Be specific.
        2. department: The department name (e.g., 'R&D', 'Logistics', 'Customer Success').
        3. confidence: A float from 0.0 to 1.0 representing your certainty of the industry/department classification.
        4. culture: 'high_context' or 'low_context'
        5. formality: 'formal', 'informal', or 'casual'
        6. key_entities: Detect industry/department specific keywords.
        7. dynamic_safety_rules: Identify 2-3 specific rules that should be enforced in this context.

        """

        try:
            profile = await self.provider.chat_completion(
                response_model=ContextProfile,
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
            )
            logger.info("context_sensed", industry=profile.industry, culture=profile.culture)
            return profile
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("context_sensing_failed")
            return ContextProfile(
                industry=IndustryType.GENERIC,
                culture=CulturalContext.LOW_CONTEXT,
                formality=FormalityLevel.INFORMAL,
                reasoning="Automatic sensing failed (see logs for details).",
            )
