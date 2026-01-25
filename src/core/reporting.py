from src.schemas.performance import SlippageAnalysis, TruthGapAnalysis
from src.schemas.agents import UserHistory
from datetime import datetime


class AuditReportGenerator:
    """
    The 'Cash Generator': Turns raw database data and agent analysis into a 
    professional PDF/JSON report that can be sold as a service.
    """

    @staticmethod
    def generate_audit_summary(
        user: UserHistory,
        slippage: SlippageAnalysis,
        truth_gap: TruthGapAnalysis
    ) -> dict:
        """
        Creates a high-value 'Performance Integrity Audit' for a manager.
        """
        return {
            "report_id": f"AUDIT-{datetime.now().strftime('%Y%m%d')}-{user.user_id}",
            "generated_at": datetime.now().isoformat(),
            "subject": {
                "user_id": user.user_id,
                "reliability_score": f"{user.reliability_score:.2f}%",
                "total_commitments": user.total_commitments
            },
            "performance_metrics": {
                "status": slippage.status,
                "fulfillment_ratio": f"{slippage.fulfillment_ratio * 100:.2f}%",
                "detected_gap": slippage.detected_gap
            },
            "integrity_score": {
                "aligned": not truth_gap.gap_detected,
                "truth_score": f"{truth_gap.truth_score * 100:.2f}%",
                "explanation": truth_gap.explanation
            },
            "intervention_recommendation": {
                "required": slippage.intervention_required or truth_gap.gap_detected,
                "tone": truth_gap.recommended_tone,
                "summary": "High risk of technical debt accumulation detected." if truth_gap.gap_detected else "Maintain current performance."
            }
        }
