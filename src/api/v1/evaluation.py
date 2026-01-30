# Copyright (c) 2026 CommitVigil AI. All rights reserved.

from arq import ArqRedis
from fastapi import APIRouter, Depends, HTTPException
from fastapi_limiter.depends import RateLimiter

from src.api.deps import get_api_key, get_redis
from src.core.config import settings
from src.core.logging import logger
from src.schemas.agents import CommitmentUpdate

router = APIRouter()


@router.post(
    "/evaluate",
    dependencies=[Depends(get_api_key), Depends(RateLimiter(times=10, seconds=60))],
)
async def evaluate_commitment(
    update: CommitmentUpdate,
    sync: bool = False,
    redis: ArqRedis = Depends(get_redis),  # noqa: B008
):
    """
    Main ingestion gateway for commitment evaluations.
    - Production (Default): Enqueues job in Redis for background processing.
    - Sync Mode (sync=true): Executes pipeline immediately (useful for demos and low-latency chatbots).
    """
    from src.agents.brain import CommitVigilBrain
    from src.core.database import get_user_reliability

    if sync:
        logger.info("synchronous_evaluation_triggered", user_id=update.user_id)
        brain = CommitVigilBrain()
        reliability, slack_id, consecutive_firm = await get_user_reliability(update.user_id)

        try:
            evaluation = await brain.evaluate_participation(
                user_id=update.user_id,
                check_in=update.check_in,
                reliability_score=reliability,
                consecutive_firm=consecutive_firm,
                industry=update.industry,
            )
            return evaluation
        except Exception as e:
            logger.error("sync_evaluation_failed", error=str(e), user_id=update.user_id)
            error_detail = (
                str(e)
                if settings.DEMO_MODE
                else "An internal reasoning error occurred. Please try again later."
            )
            raise HTTPException(status_code=500, detail=error_detail) from None

    # Offload the Agentic work to the background worker (Production Path)
    job = await redis.enqueue_job(
        "process_commitment_eval",
        user_id=update.user_id,
        commitment=update.commitment,
        check_in=update.check_in,
        industry=update.industry,
    )

    if job:
        logger.info("commitment_enqueued", user_id=update.user_id, job_id=job.job_id)
        return {
            "status": "enqueued",
            "job_id": job.job_id,
            "message": "The Accountability Agent is analyzing your update in the background.",
        }
