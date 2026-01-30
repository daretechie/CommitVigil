# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from datetime import datetime, timedelta, timezone

from sqlmodel import func, select

from src.core.database import AsyncSessionLocal
from src.core.logging import logger
from src.core.state import state
from src.schemas.agents import SafetyFeedback


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
        notes: str | None = None,
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
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            session.add(feedback)
            await session.commit()

        logger.info(
            "feedback_persisted",
            intervention_id=intervention_id,
            action=action,
            manager=manager_id,
        )

    @staticmethod
    async def calculate_intervention_acceptance(days: int = 30) -> float:
        """
        ROI Metric: Calculates the percentage of AI corrections accepted by managers.
        Includes 1-hour Redis caching to prevent database thrashing.
        """
        cache_key = f"acceptance_rate:{days}"
        redis = state.get("redis")

        # 1. Check Cache
        if redis:
            try:
                cached = await redis.get(cache_key)
                if cached:
                    return float(cached)
            except Exception as e:
                logger.warning("acceptance_rate_cache_peek_failed", error=str(e))

        # 2. Database Calculation (Aggregated)
        since = (datetime.now(timezone.utc) - timedelta(days=days)).replace(tzinfo=None)
        async with AsyncSessionLocal() as session:
            # Optimized: Single query for both counts
            statement = select(
                func.count(SafetyFeedback.id),
                func.count(SafetyFeedback.id).filter(SafetyFeedback.action_taken == "accepted")
            ).where(SafetyFeedback.created_at >= since)
            
            result = await session.execute(statement)
            total, accepted = result.one()
            
            rate = round(accepted / total, 2) if total > 0 else 1.0

        # 3. Update Cache
        if redis:
            try:
                # Cache for 1 hour
                await redis.setex(cache_key, 3600, str(rate))
            except Exception as e:
                logger.warning("acceptance_rate_cache_population_failed", error=str(e))

        return rate

    @staticmethod
    async def get_audit_trail(intervention_id: str) -> SafetyFeedback | None:
        """
        Governance Feature: Retrieves the full audit trail for a specific intervention.
        """
        async with AsyncSessionLocal() as session:
            statement = select(SafetyFeedback).where(
                SafetyFeedback.intervention_id == intervention_id
            )
            result = await session.execute(statement)
            return result.scalar_one_or_none()
