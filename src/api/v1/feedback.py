# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from fastapi import APIRouter, Depends, HTTPException

from src.agents.learning import SupervisorFeedbackLoop
from src.api.deps import get_api_key
from src.core.logging import logger
from src.schemas.agents import CorrectionFeedback

router = APIRouter()


@router.post("/feedback", dependencies=[Depends(get_api_key)])
async def log_manager_feedback(feedback: CorrectionFeedback):
    """
    Human-in-the-Loop: Managers providing feedback on interventions.
    This feedback tunes the model's future safety decisions.
    """
    try:
        loop = SupervisorFeedbackLoop()
        await loop.log_manager_decision(
            intervention_id=feedback.intervention_id,
            user_id=feedback.user_id,
            manager_id=feedback.manager_id,
            action=feedback.action_taken,
            message=feedback.final_message_sent,
            notes=feedback.comments,
        )
        logger.info(
            "manager_feedback_logged",
            intervention_id=feedback.intervention_id,
            action=feedback.action_taken,
        )
        return {
            "status": "success",
            "message": "Feedback integrated into continuous learning loop.",
        }
    except Exception as e:
        logger.error("feedback_logging_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to persist feedback.") from e
