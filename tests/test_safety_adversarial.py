from unittest.mock import AsyncMock, patch

import pytest

from src.agents.brain import CommitVigilBrain
from src.agents.safety import SafetyAudit
from src.schemas.agents import (
    AgentDecision,
    BurnoutDetection,
    ExcuseAnalysis,
    ExcuseCategory,
    RiskAssessment,
    RiskLevel,
    ToneType,
)


@pytest.fixture(autouse=True)
def force_mock_settings(request):
    """Ensure settings are correct for this module, regardless of other tests."""
    if request.config.getoption("--run-live"):
        yield
        return

    from src.core.config import settings

    orig_provider = settings.LLM_PROVIDER
    orig_key = settings.OPENAI_API_KEY

    settings.LLM_PROVIDER = "mock"
    settings.OPENAI_API_KEY = None

    yield

    settings.LLM_PROVIDER = orig_provider
    settings.OPENAI_API_KEY = orig_key


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
    burnout = BurnoutDetection(is_at_risk=False, sentiment_indicators=[], recommendation="rest")
    return decision, excuse, risk, burnout


def apply_standard_mocks(brain, excuse, risk, burnout):
    brain.analyze_excuse = AsyncMock(return_value=excuse)
    brain.detect_burnout = AsyncMock(return_value=burnout)
    brain.assess_risk = AsyncMock(return_value=risk)


@pytest.mark.asyncio
async def test_adversarial_hard_block_salary(mock_brain_components):
    """Test that HR/Salary talk triggers a hard block and HitL."""
    decision, excuse, risk, burnout = mock_brain_components
    # Mock Safety Supervisor to return HARD BLOCK
    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        brain = CommitVigilBrain()  # Move inside patch

        # Mock Steps 1 & 2 with VALID Pydantic Models
        brain.analyze_excuse = AsyncMock(return_value=excuse)  # type: ignore[method-assign]
        brain.detect_burnout = AsyncMock(return_value=burnout)  # type: ignore[method-assign]
        brain.assess_risk = AsyncMock(return_value=risk)  # type: ignore[method-assign]

        # Decision must mock the "bad" message we want to audit
        bad_decision = decision.model_copy()
        bad_decision.message = "We need to discuss your salary reduction."
        brain.adapt_tone = AsyncMock(return_value=bad_decision)  # type: ignore[method-assign]

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
        assert result.safety_audit is not None
        assert result.safety_audit.intervention_type == "block"
        assert "blocked for manual manager review" in result.decision.message


@pytest.mark.asyncio
async def test_adversarial_low_confidence_idiom(mock_brain_components):
    """Test that low supervisor confidence triggers HitL."""
    decision, excuse, risk, burnout = mock_brain_components
    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        brain = CommitVigilBrain()

        brain.analyze_excuse = AsyncMock(return_value=excuse)  # type: ignore[method-assign]
        brain.detect_burnout = AsyncMock(return_value=burnout)  # type: ignore[method-assign]
        brain.assess_risk = AsyncMock(return_value=risk)  # type: ignore[method-assign]

        idiom_decision = decision.model_copy()
        idiom_decision.message = "You need to bite the bullet."
        brain.adapt_tone = AsyncMock(return_value=idiom_decision)  # type: ignore[method-assign]

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
            f"[Test Output] Final Decision: Action='{result.decision.action}', Intervention='{result.safety_audit.intervention_type if result.safety_audit else 'None'}'"
        )

        assert result.decision.action == "escalate_to_manager"
        assert result.safety_audit is not None
        assert result.safety_audit.intervention_type == "review"
        assert result.safety_audit.reasoning is not None  # type: ignore[union-attr]
        assert "Confidence below threshold" in result.safety_audit.reasoning


@pytest.mark.asyncio
async def test_adversarial_allowed_pricing(mock_brain_components):
    """Test that 'Pricing' discussion is ALLOWED (Not Hard Blocked)."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitVigilBrain()

    brain.analyze_excuse = AsyncMock(return_value=excuse)  # type: ignore[method-assign]
    brain.detect_burnout = AsyncMock(return_value=burnout)  # type: ignore[method-assign]
    brain.assess_risk = AsyncMock(return_value=risk)  # type: ignore[method-assign]

    pricing_decision = decision.model_copy()
    pricing_decision.message = "Where is the pricing proposal?"
    brain.adapt_tone = AsyncMock(return_value=pricing_decision)  # type: ignore[method-assign]

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

        assert result.decision.action == "notified"  # Assuming default action mapped nicely
        assert result.safety_audit is None  # No intervention


@pytest.mark.asyncio
async def test_hybrid_correction_injection(mock_brain_components):
    """Test that a soft correction is injected and logged."""
    decision, excuse, risk, burnout = mock_brain_components
    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        brain = CommitVigilBrain()

        brain.analyze_excuse = AsyncMock(return_value=excuse)  # type: ignore[method-assign]
        brain.detect_burnout = AsyncMock(return_value=burnout)  # type: ignore[method-assign]
        brain.assess_risk = AsyncMock(return_value=risk)  # type: ignore[method-assign]

        harsh_decision = decision.model_copy()
        harsh_decision.message = "Do it now."
        brain.adapt_tone = AsyncMock(return_value=harsh_decision)  # type: ignore[method-assign]

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

        async def side_effect(_msg, _tone, _ctx, *_args, **_kwargs):
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
        assert result.safety_audit is not None
        assert result.safety_audit.intervention_type == "correction"
        assert result.safety_audit.reasoning is not None  # type: ignore[union-attr]
        assert result.safety_audit.intervention_type == "correction"  # type: ignore[union-attr]

        assert result.safety_audit.original_message == "Do it now."


@pytest.mark.asyncio
async def test_nested_hr_context(mock_brain_components):
    """Test 6: Message contains 'salary' but in valid client context -> ALLOWED."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitVigilBrain()

    brain.analyze_excuse = AsyncMock(return_value=excuse)  # type: ignore[method-assign]
    brain.detect_burnout = AsyncMock(return_value=burnout)  # type: ignore[method-assign]
    brain.assess_risk = AsyncMock(return_value=risk)  # type: ignore[method-assign]

    nested_hr_msg = decision.model_copy()
    nested_hr_msg.message = (
        "The client asked about our team's salary expectations for the project bid."
    )
    brain.adapt_tone = AsyncMock(return_value=nested_hr_msg)  # type: ignore[method-assign]

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
    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        brain = CommitVigilBrain()

        brain.analyze_excuse = AsyncMock(return_value=excuse)  # type: ignore[method-assign]
        brain.detect_burnout = AsyncMock(return_value=burnout)  # type: ignore[method-assign]
        brain.assess_risk = AsyncMock(return_value=risk)  # type: ignore[method-assign]

        dual_msg = decision.model_copy()
        dual_msg.message = "Finish this today or we'll discuss your performance review."
        brain.adapt_tone = AsyncMock(return_value=dual_msg)  # type: ignore[method-assign]

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
        assert result.safety_audit is not None
        assert result.safety_audit.intervention_type == "block"
        assert "blocked for manual manager review" in result.decision.message


@pytest.mark.asyncio
async def test_cultural_idiom_sensitivity(mock_brain_components):
    """Test 5: Cross-Cultural Ambiguity - Directness flagged in sensitive context."""
    decision, excuse, risk, burnout = mock_brain_components
    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        brain = CommitVigilBrain()

        brain.analyze_excuse = AsyncMock(return_value=excuse)  # type: ignore[method-assign]
        brain.detect_burnout = AsyncMock(return_value=burnout)  # type: ignore[method-assign]
        brain.assess_risk = AsyncMock(return_value=risk)  # type: ignore[method-assign]

        direct_msg = decision.model_copy()
        direct_msg.message = "Please consider this carefully."
        brain.adapt_tone = AsyncMock(return_value=direct_msg)  # type: ignore[method-assign]

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

        async def side_effect(_msg, _tone, _ctx, *_args, **_kwargs):
            return [initial_audit, re_audit][mock_instance.audit_message.call_count - 1]

        mock_instance.audit_message.side_effect = side_effect

        print(f"\n[Test Output] Input Message: '{direct_msg.message}'")
        result = await brain.evaluate_participation("u1", "status", 100.0, 0)
        print(
            f"[Test Output] Correction: '{result.decision.message}' (Reason: {result.safety_audit.reasoning if result.safety_audit else 'None'})"
        )

        assert result.decision.message == "Perhaps we could reflect on this together?"
        audit = result.safety_audit
        assert audit is not None
        assert audit.reasoning is not None
        assert audit.intervention_type == "correction"


@pytest.mark.asyncio
async def test_no_infinite_corrections(mock_brain_components):
    """Test 7: No Infinite Loops - Verify Supervisor is called exactly ONCE per cycle."""
    decision, excuse, risk, burnout = mock_brain_components
    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        brain = CommitVigilBrain()

        brain.analyze_excuse = AsyncMock(return_value=excuse)  # type: ignore[method-assign]
        brain.detect_burnout = AsyncMock(return_value=burnout)  # type: ignore[method-assign]
        brain.assess_risk = AsyncMock(return_value=risk)  # type: ignore[method-assign]
        brain.adapt_tone = AsyncMock(return_value=decision)  # type: ignore[method-assign]

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

        async def side_effect(_msg, _tone, _ctx, *_args, **_kwargs):
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
    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        brain = CommitVigilBrain()

        brain.analyze_excuse = AsyncMock(return_value=excuse)  # type: ignore[method-assign]
        brain.detect_burnout = AsyncMock(return_value=burnout)  # type: ignore[method-assign]
        brain.assess_risk = AsyncMock(return_value=risk)  # type: ignore[method-assign]

        uk_msg = decision.model_copy()
        uk_msg.message = "You need to pull your socks up."
        brain.adapt_tone = AsyncMock(return_value=uk_msg)  # type: ignore[method-assign]

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
            f"[Test Output] Action: '{result.decision.action}' (Reason: {result.safety_audit.reasoning if result.safety_audit else 'None'})"
        )

        assert result.decision.action == "escalate_to_manager"
        assert result.safety_audit is not None
        assert result.safety_audit.intervention_type == "review"  # type: ignore[union-attr]


@pytest.mark.asyncio
async def test_supervisor_catches_bad_correction(mock_brain_components):
    """
    Test 10: Safety Valve (Correction Re-Validation).
    Brain generates unsafe msg -> Supervisor suggests UNSAFE correction -> Re-audit catches it -> HITL.
    """
    decision, excuse, risk, burnout = mock_brain_components
    with patch("src.agents.brain.SafetySupervisor") as MockSupervisor:
        mock_instance = MockSupervisor.return_value
        brain = CommitVigilBrain()

        brain.analyze_excuse = AsyncMock(return_value=excuse)  # type: ignore[method-assign]
        brain.detect_burnout = AsyncMock(return_value=burnout)  # type: ignore[method-assign]
        brain.assess_risk = AsyncMock(return_value=risk)  # type: ignore[method-assign]

        toxic_msg = decision.model_copy()
        toxic_msg.message = "Do it now or you're fired."
        brain.adapt_tone = AsyncMock(return_value=toxic_msg)  # type: ignore[method-assign]

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
        async def side_effect(_msg, _tone, _ctx, *_args, **_kwargs):
            return [audit_1, audit_2][mock_instance.audit_message.call_count - 1]

        mock_instance.audit_message.side_effect = side_effect

        print("\n[Test Output] Verifying Safety Valve (Re-Audit)...")

        result = await brain.evaluate_participation("u1", "status", 100.0, 0)
        print(f"[Test Output] Final Action: '{result.decision.action}'")
        print(
            f"[Test Output] Reasoning: '{result.safety_audit.reasoning if result.safety_audit else 'None'}'"
        )

        # VERIFICATION
        assert mock_instance.audit_message.call_count == 2  # Proves re-audit happened
        assert result.decision.action == "escalate_to_manager"  # Fallback to HITL
        audit = result.safety_audit
        assert audit is not None
        assert audit.intervention_type == "review"
        assert audit.reasoning is not None
        assert "Safety Valve Triggered" in audit.reasoning


@pytest.mark.asyncio
async def test_cultural_persona_wa_japanese(mock_brain_components):
    """Phase 15: Verify Japanese 'Wa' persona (Polite Suggestion)."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitVigilBrain()

    # Mock LLM to return a very polite, indirect Japanese decision
    wa_decision = decision.model_copy()
    wa_decision.message = "It might be helpful to reflect on our progress together."
    wa_decision.tone = ToneType.SUPPORTIVE

    apply_standard_mocks(brain, excuse, risk, burnout)
    brain.adapt_tone = AsyncMock(return_value=wa_decision)  # type: ignore[method-assign]

    print("\n[Test Output] Testing Japanese 'Wa' Persona...")
    result = await brain.evaluate_participation("u1", "status", 100.0, 0, lang="ja")

    assert result.decision.tone == ToneType.SUPPORTIVE
    assert "reflect" in result.decision.message
    print(f"[Test Output] Final Tone: {result.decision.tone} | Msg: {result.decision.message}")


@pytest.mark.asyncio
async def test_cultural_persona_sachlichkeit_german(mock_brain_components):
    """Phase 15: Verify German 'Sachlichkeit' persona (Direct/Objective)."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitVigilBrain()

    # Mock LLM to return a direct, objective German decision
    sach_decision = decision.model_copy()
    sach_decision.message = "The metric for completion is not met. Objective assessment required."
    sach_decision.tone = ToneType.NEUTRAL

    apply_standard_mocks(brain, excuse, risk, burnout)
    brain.adapt_tone = AsyncMock(return_value=sach_decision)  # type: ignore[method-assign]

    print("\n[Test Output] Testing German 'Sachlichkeit' Persona...")
    result = await brain.evaluate_participation("u1", "status", 80.0, 0, lang="de")

    assert result.decision.tone == ToneType.NEUTRAL
    assert "metric" in result.decision.message
    print(f"[Test Output] Final Tone: {result.decision.tone} | Msg: {result.decision.message}")


@pytest.mark.asyncio
async def test_cultural_persona_ubuntu_af(mock_brain_components):
    """Phase 15: Verify African Ubuntu persona (Communal Responsibility)."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitVigilBrain()

    # Mock LLM to return a communal, Ubuntu-inspired decision
    ubuntu_decision = decision.model_copy()
    ubuntu_decision.message = (
        "When one of us pauses, our entire village (the team) feels the weight."
    )
    ubuntu_decision.tone = ToneType.SUPPORTIVE

    apply_standard_mocks(brain, excuse, risk, burnout)
    brain.adapt_tone = AsyncMock(return_value=ubuntu_decision)  # type: ignore[method-assign]

    print("\n[Test Output] Testing African 'Ubuntu' Persona...")
    result = await brain.evaluate_participation("u1", "status", 90.0, 0, lang="en-AF")

    assert result.decision.tone == ToneType.SUPPORTIVE
    assert "village" in result.decision.message
    print(f"[Test Output] Final Tone: {result.decision.tone} | Msg: {result.decision.message}")


@pytest.mark.asyncio
async def test_prospect_audit_generation():
    """Phase 15: Verify the Sales Prospecting Audit logic."""
    from src.core.reporting import AuditReportGenerator
    from src.schemas.agents import ProspectProfile

    profile = ProspectProfile(
        company_name="Cursor",
        target_role="CEO",
        team_size=50,
        avg_developer_salary=180000.0,
        drift_scenarios=[
            {"who": "Michael", "promise": "Finish Vibe Coding", "reality": "Just vibing"}
        ],
    )

    print("\n[Test Output] Generating Prospect Audit for Cursor...")
    report = AuditReportGenerator.generate_prospect_audit(profile)

    assert report["prospect"] == "Cursor"
    assert "roi_prediction" in report
    assert report["roi_prediction"]["annual_savings_usd"] > 0
    assert len(report["sample_interventions"]) == 1
    assert "Vibe Coding" in report["sample_interventions"][0].performance_metrics["detected_gap"]

    print(
        f"[Test Output] Predicted Annual Savings: ${report['roi_prediction']['annual_savings_usd']:,.2f}"
    )


@pytest.mark.asyncio
async def test_cultural_persona_jeitinho_brazilian(mock_brain_components):
    """Phase 16: Verify Brazilian 'Jeitinho' persona (Warm/Relationship-focused)."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitVigilBrain()

    # Mock LLM to return a warm, relationship-focused Brazilian decision
    br_decision = decision.model_copy()
    br_decision.message = (
        "Our partnership is very important to me, and I know we can find a way together."
    )
    br_decision.tone = ToneType.SUPPORTIVE

    apply_standard_mocks(brain, excuse, risk, burnout)
    brain.adapt_tone = AsyncMock(return_value=br_decision)  # type: ignore[method-assign]

    print("\n[Test Output] Testing Brazilian 'Jeitinho' Persona...")
    result = await brain.evaluate_participation("u1", "status", 95.0, 0, lang="pt-BR")

    assert result.decision.tone == ToneType.SUPPORTIVE
    assert "partnership" in result.decision.message
    print(f"[Test Output] Final Tone: {result.decision.tone} | Msg: {result.decision.message}")


@pytest.mark.asyncio
async def test_cultural_persona_guanxi_chinese(mock_brain_components):
    """Phase 16: Verify Chinese 'Guanxi' persona (Communal Face/Respectful)."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitVigilBrain()

    # Mock LLM to return a respectful, face-saving Chinese decision
    zh_decision = decision.model_copy()
    zh_decision.message = (
        "For the benefit of our collective success, let us align our efforts once more."
    )
    zh_decision.tone = ToneType.NEUTRAL

    apply_standard_mocks(brain, excuse, risk, burnout)
    brain.adapt_tone = AsyncMock(return_value=zh_decision)  # type: ignore[method-assign]

    print("\n[Test Output] Testing Chinese 'Guanxi' Persona...")
    result = await brain.evaluate_participation("u1", "status", 100.0, 0, lang="zh")

    assert result.decision.tone == ToneType.NEUTRAL
    assert "collective" in result.decision.message
    print(f"[Test Output] Final Tone: {result.decision.tone} | Msg: {result.decision.message}")


@pytest.mark.asyncio
async def test_cultural_persona_lagom_nordic(mock_brain_components):
    """Phase 16: Verify Nordic 'Lagom' persona (Balanced/Collaborative)."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitVigilBrain()

    # Mock LLM to return a balanced Nordic decision
    sv_decision = decision.model_copy()
    sv_decision.message = "We should strive for a sustainable balance in our commitments."
    sv_decision.tone = ToneType.SUPPORTIVE

    apply_standard_mocks(brain, excuse, risk, burnout)
    brain.adapt_tone = AsyncMock(return_value=sv_decision)  # type: ignore[method-assign]

    print("\n[Test Output] Testing Nordic 'Lagom' Persona...")
    result = await brain.evaluate_participation("u1", "status", 85.0, 0, lang="sv")

    assert result.decision.tone == ToneType.SUPPORTIVE
    assert "balance" in result.decision.message
    print(f"[Test Output] Final Tone: {result.decision.tone} | Msg: {result.decision.message}")


@pytest.mark.asyncio
async def test_cultural_persona_indian_professional(mock_brain_components):
    """Phase 16: Verify Indian Professional persona (Respectful/Technically Clear)."""
    decision, excuse, risk, burnout = mock_brain_components
    brain = CommitVigilBrain()

    # Mock LLM to return a respectful but technically clear Indian professional decision
    in_decision = decision.model_copy()
    in_decision.message = (
        "I would appreciate a clear update on the technical resolution for our project."
    )
    in_decision.tone = ToneType.FIRM

    apply_standard_mocks(brain, excuse, risk, burnout)
    brain.adapt_tone = AsyncMock(return_value=in_decision)  # type: ignore[method-assign]

    print("\n[Test Output] Testing Indian Professional Persona...")
    result = await brain.evaluate_participation("u1", "status", 75.0, 0, lang="en-IN")

    assert result.decision.tone == ToneType.FIRM
    assert "technical" in result.decision.message
    print(f"[Test Output] Final Tone: {result.decision.tone} | Msg: {result.decision.message}")
