from typing import Any, TypeVar, cast

from src.core.logging import logger
from src.llm.base import LLMProvider
from src.schemas.agents import (
    AgentDecision,
    BurnoutDetection,
    ExcuseAnalysis,
    ExcuseCategory,
    ExtractedCommitment,
    RiskAssessment,
    RiskLevel,
    SafetyAudit,
    SlackCommitmentRecord,
    ToneType,
)
from pydantic import BaseModel
from src.schemas.performance import SlippageAnalysis, SlippageStatus, TruthGapAnalysis

T = TypeVar("T")


class MockProvider(LLMProvider):
    """
    Elite Level Hermetic Mock Provider.
    Simulates LLM responses with basic heuristics to enable offline testing/demo.
    """

    @property
    def is_mock(self) -> bool:
        return True

    async def chat_completion(
        self, response_model: type[T], messages: list[dict[str, str]], model: str
    ) -> T:
        logger.warning("llm_mock_completion_triggered", provider="Mock", model=model)
        
        # Extract user content for heuristics
        user_content = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        ).lower()
        system_content = next(
            (m["content"] for m in messages if m["role"] == "system"), ""
        ).lower()

        # 1. Excuse Analysis Heuristics
        if response_model is ExcuseAnalysis:
            category = ExcuseCategory.DEFLECTION
            if any(w in user_content for w in ["sick", "hospital", "family"]):
                category = ExcuseCategory.LEGITIMATE
            elif any(w in user_content for w in ["tired", "exhausted", "give up"]):
                category = ExcuseCategory.BURNOUT_SIGNAL
            
            return cast(T, ExcuseAnalysis(
                category=category,
                confidence_score=0.95,
                reasoning=f"Mock: Detected keywords in '{user_content[:20]}...'",
            ))

        # 2. Risk Assessment Heuristics
        if response_model is RiskAssessment:
            return cast(T, RiskAssessment(
                risk_score=0.75,
                level=RiskLevel.HIGH,
                predicted_latency_days=3,
                mitigation_strategy="Mock: Suggest immediate PM intervention.",
            ))

        # 3. Burnout Detection Heuristics
        if response_model is BurnoutDetection:
            is_risk = any(
                w in user_content for w in ["exhausted", "cannot cope", "too much"]
            )
            return cast(T, BurnoutDetection(
                is_at_risk=is_risk,
                sentiment_indicators=["high_fatigue"] if is_risk else [],
                recommendation="Suggest time off" if is_risk else "Continues monitoring",
            ))

        # 4. Commitment Extraction Heuristics
        if response_model is ExtractedCommitment:
            return cast(T, ExtractedCommitment(
                task="Mock Task: " + user_content[:20] + "...",
                deadline="Friday 5 PM",
                confidence_score=0.88,
            ))

        # 5. Agent Decision (Tone) Heuristics
        if response_model is AgentDecision:
            # Parse context from system prompt for rudimentary state awareness
            # Format: "User Reliability: 90%"
            reliability = 100.0
            consecutive_strict = 0
            
            import re
            rel_match = re.search(r"user reliability:\s*([\d\.]+)", system_content)
            if rel_match:
                reliability = float(rel_match.group(1))
            
            strict_match = re.search(r"consecutive strict interventions:\s*(\d+)", system_content)
            if strict_match:
                consecutive_strict = int(strict_match.group(1))

            # Logic
            tone = ToneType.SUPPORTIVE
            msg = "Mock: Default supportive response."
            action = "none"

            # Check for Burnout in user content
            # The prompt sends "Burnout: is_at_risk=True ..."
            is_burnout = "is_at_risk=true" in user_content.lower()

            if is_burnout:
                tone = ToneType.SUPPORTIVE
                msg = "I hear you. It sounds like you're reaching your limit. Suggest time off."
                action = "escalate_to_manager"
            elif consecutive_strict >= 3:
                tone = ToneType.NEUTRAL
                msg = "Let's reset and focus on a small, achievable win today."
            elif reliability < 50.0:
                tone = ToneType.CONFRONTATIONAL if reliability < 20.0 else ToneType.FIRM
                msg = "This is your third delay this month. recovery plan needed."
                action = "escalate_to_manager"
            
            return cast(T, AgentDecision(
                action=action,
                tone=tone,
                message=msg,
                analysis_summary=f"Mock Decision (Rel={reliability}, Strict={consecutive_strict}, Burnout={is_burnout})",
            ))

        # 6. Performance Slippage Heuristics
        if response_model is SlippageAnalysis:
            return cast(T, SlippageAnalysis(
                status=SlippageStatus.ON_TRACK,
                fulfillment_ratio=0.9,
                detected_gap="Mock: High alignment detected.",
                risk_to_system_stability=0.1,
                intervention_required=False,
            ))

        # 7. Truth Gap Heuristics
        if response_model is TruthGapAnalysis:
            return cast(T, TruthGapAnalysis(
                gap_detected=False,
                truth_score=0.95,
                explanation="Mock: Claims match technical evidence.",
                recommended_tone="neutral",
            ))

        if response_model is SlackCommitmentRecord:
            return cast(T, SlackCommitmentRecord(
                commitment_found=True,
                who="Mock User",
                what="Refactor API structure",
                when="Next Friday 10:00 AM",
            ))

        # 10. Safety Audit Heuristics
        if response_model is SafetyAudit:
            return cast(T, SafetyAudit(
                is_safe=True,
                risk_of_morale_damage=0.05,
                supervisor_confidence=0.98,
                reasoning="Mock: Message appears professional and scoped correctly.",
            ))

        # Fallback for unknown models (generic dummy data)
        dummy_data: dict[str, Any] = {}
        # Bound T to BaseModel in base.py, but cast here for MyPy clarity
        model_cls = cast(type[BaseModel], response_model)
        
        for name, field in model_cls.model_fields.items():
            annotation = field.annotation
            if annotation is str:
                dummy_data[name] = f"mock_{name}"
            elif annotation is float:
                dummy_data[name] = 0.95
            elif annotation is int:
                dummy_data[name] = 1
            else:
                dummy_data[name] = None

        return cast(T, response_model(**dummy_data))
