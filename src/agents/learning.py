from datetime import datetime, timedelta, timezone
from sqlmodel import select, func
from src.core.database import AsyncSessionLocal
from src.schemas.agents import SafetyFeedback
from src.core.logging import logger

class SupervisorFeedbackLoop:
    """
    2026 Continuous Learning Agent: Analyzes manager overrides to improve AI calibration.
    """

    @staticmethod
    async def log_manager_decision(
        intervention_id: str,
        user_id: str,
        manager_id: str,
        action: str,
        message: str,
        notes: str | None = None
    ) -> None:
        """
        Persists manager feedback to the database for historical ROI analysis.
        """
        async with AsyncSessionLocal() as session:
            feedback = SafetyFeedback(
                intervention_id=intervention_id,
                user_id=user_id,
                manager_id=manager_id,
                action_taken=action,
                final_message_sent=message,
                feedback_notes=notes,
                created_at=datetime.now(timezone.utc)
            )
            session.add(feedback)
            await session.commit()
        
        logger.info(
            "feedback_persisted",
            intervention_id=intervention_id,
            action=action,
            manager=manager_id
        )

    @staticmethod
    async def calculate_intervention_acceptance(days: int = 30) -> float:
        """
        ROI Metric: Calculates the percentage of AI corrections accepted by managers.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)
        async with AsyncSessionLocal() as session:
            # Total count
            statement_total = select(func.count(SafetyFeedback.id)).where(SafetyFeedback.created_at >= since)
            result_total = await session.execute(statement_total)
            total = result_total.scalar() or 0
            
            if total == 0:
                return 1.0  # Default to perfect if no feedback yet
                
            # Accepted count
            statement_accepted = select(func.count(SafetyFeedback.id)).where(
                SafetyFeedback.created_at >= since,
                SafetyFeedback.action_taken == "accepted"
            )
            result_accepted = await session.execute(statement_accepted)
            accepted = result_accepted.scalar() or 0
            
            return round(accepted / total, 2)

    @staticmethod
    async def get_audit_trail(intervention_id: str) -> SafetyFeedback | None:
        """
        Governance Feature: Retrieves the full audit trail for a specific intervention.
        """
        async with AsyncSessionLocal() as session:
            statement = select(SafetyFeedback).where(SafetyFeedback.intervention_id == intervention_id)
            result = await session.execute(statement)
            return result.scalar_one_or_none()
