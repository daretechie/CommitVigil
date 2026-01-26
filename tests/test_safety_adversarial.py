import pytest
from unittest.mock import AsyncMock, patch
from src.agents.brain import CommitGuardBrain
from src.agents.safety import SafetyAudit

from src.schemas.agents import (
    ToneType,
    AgentDecision,
    ExcuseAnalysis,
    ExcuseCategory,
    RiskAssessment,
    RiskLevel,
    BurnoutDetection,
)


@pytest.fixture
def mock_brain_components():
    """Setup standard decision mocked components"""
    decision = AgentDecision(
        action="notified",
        tone=ToneType.FIRM,
        message="Proposed Message",
        analysis_summary="sum",
    )
    excuse = ExcuseAnalysis(
        category=ExcuseCategory.LEGITIMATE, confidence_score=0.9, reasoning="logic"
    )
    risk = RiskAssessment(
        risk_score=0.1,
        level=RiskLevel.LOW,
        predicted_latency_days=0,
        mitigation_strategy="none",
    )
    burnout = BurnoutDetection(
        is_at_risk=False, sentiment_indicators=[], recommendation="rest"
    )
    return decision, excuse, risk, burnout


@pytest.mark.asyncio
async def test_adversarial_hard_block_salary(mock_brain_components):
    """Test that HR/Salary talk triggers a hard block and HitL."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitGuardBrain()

    # Mock Steps 1 & 2 with VALID Pydantic Models
    brain.analyze_excuse = AsyncMock(return_value=excuse)
    brain.detect_burnout = AsyncMock(return_value=burnout)
    brain.assess_risk = AsyncMock(return_value=risk)

    # Decision must mock the "bad" message we want to audit
    bad_decision = decision.model_copy()
    bad_decision.message = "We need to discuss your salary reduction."
    brain.adapt_tone = AsyncMock(return_value=bad_decision)

    # Mock Safety Supervisor to return HARD BLOCK
    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        mock_instance.audit_message = AsyncMock(
            return_value=SafetyAudit(
                is_safe=False,
                is_hard_blocked=True,
                risk_of_morale_damage=0.9,
                supervisor_confidence=1.0,
                correction_type="none",
                reasoning="Salary discussion detected",
                suggested_correction=None,
            )
        )

        print(f"\n[Test Output] Input Message: '{bad_decision.message}'")
        result = await brain.evaluate_participation("u1", "status", 100.0, 0)
        print(
            f"[Test Output] Final Decision: Action='{result.decision.action}', Message='{result.decision.message}'"
        )

        assert result.decision.action == "escalate_to_manager"
        assert result.safety_audit.intervention_type == "block"
        assert "blocked for manual manager review" in result.decision.message


@pytest.mark.asyncio
async def test_adversarial_low_confidence_idiom(mock_brain_components):
    """Test that low supervisor confidence triggers HitL."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitGuardBrain()

    brain.analyze_excuse = AsyncMock(return_value=excuse)
    brain.detect_burnout = AsyncMock(return_value=burnout)
    brain.assess_risk = AsyncMock(return_value=risk)

    idiom_decision = decision.model_copy()
    idiom_decision.message = "You need to bite the bullet."
    brain.adapt_tone = AsyncMock(return_value=idiom_decision)

    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        mock_instance.audit_message = AsyncMock(
            return_value=SafetyAudit(
                is_safe=True,
                supervisor_confidence=0.65,  # Below 0.8 Threshold
                risk_of_morale_damage=0.2,
                reasoning="Ambiguous idiom 'bite the bullet'",
            )
        )

        print(f"\n[Test Output] Input Message: '{idiom_decision.message}'")
        result = await brain.evaluate_participation("u1", "status", 100.0, 0)
        print(
            f"[Test Output] Final Decision: Action='{result.decision.action}', Intervention='{result.safety_audit.intervention_type}'"
        )

        assert result.decision.action == "escalate_to_manager"
        assert result.safety_audit.intervention_type == "review"
        assert "Confidence below threshold" in result.safety_audit.reasoning


@pytest.mark.asyncio
async def test_adversarial_allowed_pricing(mock_brain_components):
    """Test that 'Pricing' discussion is ALLOWED (Not Hard Blocked)."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitGuardBrain()

    brain.analyze_excuse = AsyncMock(return_value=excuse)
    brain.detect_burnout = AsyncMock(return_value=burnout)
    brain.assess_risk = AsyncMock(return_value=risk)

    pricing_decision = decision.model_copy()
    pricing_decision.message = "Where is the pricing proposal?"
    brain.adapt_tone = AsyncMock(return_value=pricing_decision)

    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        mock_instance.audit_message = AsyncMock(
            return_value=SafetyAudit(
                is_safe=True,
                is_hard_blocked=False,
                supervisor_confidence=0.95,
                risk_of_morale_damage=0.0,
                reasoning="Business context allowed",
            )
        )

        print(f"\n[Test Output] Input Message: '{pricing_decision.message}'")
        result = await brain.evaluate_participation("u1", "status", 100.0, 0)
        print(
            f"[Test Output] Final Decision: Action='{result.decision.action}', Message='{result.decision.message}'"
        )

        assert (
            result.decision.action == "notified"
        )  # Assuming default action mapped nicely
        assert result.safety_audit is None  # No intervention


@pytest.mark.asyncio
async def test_hybrid_correction_injection(mock_brain_components):
    """Test that a soft correction is injected and logged."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitGuardBrain()

    brain.analyze_excuse = AsyncMock(return_value=excuse)
    brain.detect_burnout = AsyncMock(return_value=burnout)
    brain.assess_risk = AsyncMock(return_value=risk)

    harsh_decision = decision.model_copy()
    harsh_decision.message = "Do it now."
    brain.adapt_tone = AsyncMock(return_value=harsh_decision)

    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        initial_audit = SafetyAudit(
            is_safe=False,
            is_hard_blocked=False,
            supervisor_confidence=0.90,
            risk_of_morale_damage=0.6,
            correction_type="surgical",
            reasoning="Too aggressive",
            suggested_correction="could you please update us?",
        )

        re_audit = SafetyAudit(
            is_safe=True,  # Valid correction
            is_hard_blocked=False,
            supervisor_confidence=0.95,
            risk_of_morale_damage=0.1,
            correction_type="none",
            reasoning="Correction is safe.",
        )

        async def side_effect(_msg, _tone, _ctx):
            return [initial_audit, re_audit][mock_instance.audit_message.call_count - 1]

        mock_instance.audit_message.side_effect = side_effect

        print(f"\n[Test Output] Input Message: '{harsh_decision.message}'")
        # Simulate logic for hybrid vs rewrite based on length or other heuristic if implemented
        # For now, just confirming replacement
        result = await brain.evaluate_participation("u1", "status", 100.0, 0)
        print(
            f"[Test Output] Final Decision: Message='{result.decision.message}' (Original: '{harsh_decision.message}')"
        )

        # KEY: Capitalization Hook should have run ('could' -> 'Could')
        assert result.decision.message == "Could you please update us?"
        assert result.safety_audit.intervention_type == "correction"

        assert result.safety_audit.original_message == "Do it now."


@pytest.mark.asyncio
async def test_nested_hr_context(mock_brain_components):
    """Test 6: Message contains 'salary' but in valid client context -> ALLOWED."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitGuardBrain()

    brain.analyze_excuse = AsyncMock(return_value=excuse)
    brain.detect_burnout = AsyncMock(return_value=burnout)
    brain.assess_risk = AsyncMock(return_value=risk)

    nested_hr_msg = decision.model_copy()
    nested_hr_msg.message = (
        "The client asked about our team's salary expectations for the project bid."
    )
    brain.adapt_tone = AsyncMock(return_value=nested_hr_msg)

    # Simulator: LLM realizes this is external prompt, not internal HR violation
    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        mock_instance.audit_message = AsyncMock(
            return_value=SafetyAudit(
                is_safe=True,
                is_hard_blocked=False,  # Crucial: Not blocked
                supervisor_confidence=0.92,
                risk_of_morale_damage=0.0,
                reasoning="Context is client bid, not employee compensation discussion.",
            )
        )

        print(f"\n[Test Output] Input Message: '{nested_hr_msg.message}'")
        result = await brain.evaluate_participation("u1", "status", 100.0, 0)
        print(
            f"[Test Output] Safety Reasoning: '{result.decision.analysis_summary}'"
        )  # Should not have intervention text
        print(f"[Test Output] Final Status: Hard Blocked? {False}")

        assert result.safety_audit is None
        assert result.decision.message == nested_hr_msg.message


@pytest.mark.asyncio
async def test_multiple_issues_dual_violation(mock_brain_components):
    """Test 8: Message has both aggressive tone AND HR violation -> HARD BLOCK wins."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitGuardBrain()

    brain.analyze_excuse = AsyncMock(return_value=excuse)
    brain.detect_burnout = AsyncMock(return_value=burnout)
    brain.assess_risk = AsyncMock(return_value=risk)

    dual_msg = decision.model_copy()
    dual_msg.message = "Finish this today or we'll discuss your performance review."
    brain.adapt_tone = AsyncMock(return_value=dual_msg)

    # Simulator: Supervisor flags BOTH, but Hard Block is the dominant trait
    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        mock_instance.audit_message = AsyncMock(
            return_value=SafetyAudit(
                is_safe=False,  # Tone issue
                is_hard_blocked=True,  # HR issue
                supervisor_confidence=0.99,
                risk_of_morale_damage=0.95,
                reasoning="Performance threat + HR boundary violation.",
                suggested_correction="Let's ensure we finish this.",  # Even if correction exists, Block should win
            )
        )

        print(f"\n[Test Output] Input Message: '{dual_msg.message}'")
        result = await brain.evaluate_participation("u1", "status", 100.0, 0)
        print(f"[Test Output] Final Action: '{result.decision.action}'")

        # Verify Hard Block precedence
        assert result.decision.action == "escalate_to_manager"
        assert result.safety_audit.intervention_type == "block"
        assert "blocked for manual manager review" in result.decision.message


@pytest.mark.asyncio
async def test_cultural_idiom_sensitivity(mock_brain_components):
    """Test 5: Cross-Cultural Ambiguity - Directness flagged in sensitive context."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitGuardBrain()

    brain.analyze_excuse = AsyncMock(return_value=excuse)
    brain.detect_burnout = AsyncMock(return_value=burnout)
    brain.assess_risk = AsyncMock(return_value=risk)

    direct_msg = decision.model_copy()
    direct_msg.message = "Please consider this carefully."
    brain.adapt_tone = AsyncMock(return_value=direct_msg)

    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        initial_audit = SafetyAudit(
            is_safe=False,
            is_hard_blocked=False,
            supervisor_confidence=0.88,
            risk_of_morale_damage=0.4,
            correction_type="surgical",
            reasoning="Too direct for high-context cultural setting.",
            suggested_correction="Perhaps we could reflect on this together?",
        )

        re_audit = SafetyAudit(
            is_safe=True,  # Correction is good
            is_hard_blocked=False,
            supervisor_confidence=0.95,
            risk_of_morale_damage=0.1,
            correction_type="none",
            reasoning="Culturally appropriate.",
        )

        async def side_effect(_msg, _tone, _ctx):
            return [initial_audit, re_audit][mock_instance.audit_message.call_count - 1]

        mock_instance.audit_message.side_effect = side_effect

        print(f"\n[Test Output] Input Message: '{direct_msg.message}'")
        result = await brain.evaluate_participation("u1", "status", 100.0, 0)
        print(
            f"[Test Output] Correction: '{result.decision.message}' (Reason: {result.safety_audit.reasoning})"
        )

        assert result.decision.message == "Perhaps we could reflect on this together?"
        assert result.safety_audit.intervention_type == "correction"


@pytest.mark.asyncio
async def test_no_infinite_corrections(mock_brain_components):
    """Test 7: No Infinite Loops - Verify Supervisor is called exactly ONCE per cycle."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitGuardBrain()

    brain.analyze_excuse = AsyncMock(return_value=excuse)
    brain.detect_burnout = AsyncMock(return_value=burnout)
    brain.assess_risk = AsyncMock(return_value=risk)
    brain.adapt_tone = AsyncMock(return_value=decision)

    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        # Even if unsafe, we correct once and stop.
        initial_audit = SafetyAudit(
            is_safe=False,
            is_hard_blocked=False,
            supervisor_confidence=0.9,
            risk_of_morale_damage=0.5,
            correction_type="surgical",
            reasoning="Mock Unsafe",
            suggested_correction="Safe Message",
        )

        re_audit = SafetyAudit(
            is_safe=True,  # Valid correction
            is_hard_blocked=False,
            supervisor_confidence=0.95,
            risk_of_morale_damage=0.0,
            correction_type="none",
            reasoning="Re-audit passed",
        )

        async def side_effect(_msg, _tone, _ctx):
            return [initial_audit, re_audit][mock_instance.audit_message.call_count - 1]

        mock_instance.audit_message.side_effect = side_effect

        print("\n[Test Output] Verifying Single-Pass Architecture...")

        result = await brain.evaluate_participation("u1", "status", 100.0, 0)

        # KEY ASSERTION: audit_message called exactly TWICE (Initial + Re-Validation)

        # KEY ASSERTION: audit_message called exactly TWICE (Initial + Re-Validation)
        # It should NOT be called 3+ times (no infinite loop).
        assert mock_instance.audit_message.call_count == 2
        print(
            f"[Test Output] Supervisor Call Count: {mock_instance.audit_message.call_count} (Pass)"
        )

        assert result.decision.message == "Safe Message"


@pytest.mark.asyncio
async def test_uk_idioms(mock_brain_components):
    """Test 9: Regional Idiom Variations - Low confidence triggers Review."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitGuardBrain()

    brain.analyze_excuse = AsyncMock(return_value=excuse)
    brain.detect_burnout = AsyncMock(return_value=burnout)
    brain.assess_risk = AsyncMock(return_value=risk)

    uk_msg = decision.model_copy()
    uk_msg.message = "You need to pull your socks up."
    brain.adapt_tone = AsyncMock(return_value=uk_msg)

    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        # Supervisor is confused by the idiom -> Low Confidence
        mock_instance.audit_message = AsyncMock(
            return_value=SafetyAudit(
                is_safe=True,  # Might be safe, but we aren't sure
                is_hard_blocked=False,
                supervisor_confidence=0.6,  # < 0.8 Threshold
                risk_of_morale_damage=0.3,
                reasoning="Unfamiliar idiom 'pull your socks up'",
            )
        )

        print(f"\n[Test Output] Input Message: '{uk_msg.message}'")
        result = await brain.evaluate_participation("u1", "status", 100.0, 0)
        print(
            f"[Test Output] Action: '{result.decision.action}' (Reason: {result.safety_audit.reasoning})"
        )

        assert result.decision.action == "escalate_to_manager"
        assert result.safety_audit.intervention_type == "review"


@pytest.mark.asyncio
async def test_supervisor_catches_bad_correction(mock_brain_components):
    """
    Test 10: Safety Valve (Correction Re-Validation).
    Brain generates unsafe msg -> Supervisor suggests UNSAFE correction -> Re-audit catches it -> HITL.
    """
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitGuardBrain()

    brain.analyze_excuse = AsyncMock(return_value=excuse)
    brain.detect_burnout = AsyncMock(return_value=burnout)
    brain.assess_risk = AsyncMock(return_value=risk)

    toxic_msg = decision.model_copy()
    toxic_msg.message = "Do it now or you're fired."
    brain.adapt_tone = AsyncMock(return_value=toxic_msg)

    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value

        # MOCK CHAIN:
        # 1. First Audit: Unsafe, suggests a correction that is ALSO unsafe (adversarial AI failure).
        # 2. Second Audit (Re-validation): Detects the correction is unsafe.

        audit_1 = SafetyAudit(
            is_safe=False,
            is_hard_blocked=False,  # Let it try to correct
            correction_type="surgical",
            supervisor_confidence=0.9,
            risk_of_morale_damage=0.8,
            reasoning="Too aggressive",
            suggested_correction="Please prioritize or face consequences.",  # Still threatening!
        )

        audit_2 = SafetyAudit(
            is_safe=False,  # Re-audit Fails!
            is_hard_blocked=False,  # Wait, logic needs to be careful here
            correction_type="none",
            supervisor_confidence=0.95,
            risk_of_morale_damage=0.9,
            reasoning="Still contains implied threat.",
        )

        # Configure side_effect with a callable that returns the next item
        async def side_effect(_msg, _tone, _ctx):
            return [audit_1, audit_2][mock_instance.audit_message.call_count - 1]

        mock_instance.audit_message.side_effect = side_effect

        print("\n[Test Output] Verifying Safety Valve (Re-Audit)...")

        result = await brain.evaluate_participation("u1", "status", 100.0, 0)
        print(f"[Test Output] Final Action: '{result.decision.action}'")
        print(f"[Test Output] Reasoning: '{result.safety_audit.reasoning}'")

        # VERIFICATION
        assert mock_instance.audit_message.call_count == 2  # Proves re-audit happened
        assert result.decision.action == "escalate_to_manager"  # Fallback to HITL
        assert result.safety_audit.intervention_type == "review"
        assert "Safety Valve Triggered" in result.safety_audit.reasoning
