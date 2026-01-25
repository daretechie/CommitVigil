from arq.connections import RedisSettings
from src.core.config import settings
from src.core.logging import setup_logging, logger
from src.agents.brain import CommitGuardBrain
from src.schemas.agents import RiskLevel, ExcuseCategory
from src.core.database import init_db, get_user_reliability, update_user_reliability

from src.core.slack import SlackConnector
from apscheduler.schedulers.asyncio import AsyncIOScheduler



from datetime import datetime, timedelta

# Initialize Logging for the Worker
setup_logging()

# Initialize a persistent scheduler
scheduler = AsyncIOScheduler()


async def send_follow_up(user_id: str, message: str, slack_id: str | None = None):
    """
    Dedicated background task to handle push or chat-based notifications.
    Now sends REAL notifications to Slack.
    """
    logger.info("scheduled_follow_up_triggered", user_id=user_id, message=message)
    await SlackConnector.send_notification(message, slack_id=slack_id)



async def process_commitment_eval(
    _ctx: dict, user_id: str, commitment: str, check_in: str
):
    """
    The Main Agentic Pipeline.
    Runs behavioral analysis and schedules accountability follow-ups.
    """
    logger.info("processing_commitment_eval", user_id=user_id, status="started")

    brain = CommitGuardBrain()

    # 1. Parallel Analysis Phase (High Velocity)
    reliability, slack_id, consecutive_firm = await get_user_reliability(user_id)
    
    # 2. Executing the Orchestrated Pipeline (The Brain)
    decision = await brain.evaluate_participation(
        user_id=user_id,
        commitment=commitment,
        check_in=check_in,
        reliability_score=reliability,
        consecutive_firm=consecutive_firm
    )

    logger.info(
        "agent_pipeline_completed",
        user_id=user_id,
        action=decision.action,
        tone=decision.tone,
        final_message_preview=decision.message[:50] + "..."
    )


    # 6. Persist results for Heatmap tracking & Ethical Cooling-off state
    is_failure = excuse.category != ExcuseCategory.LEGITIMATE
    await update_user_reliability(user_id, was_failure=is_failure, tone_used=decision.tone)


    # 7. Accountability Logic: Proactive Follow-up
    # Triggered based on calculated risk thresholds
    if risk.level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        run_time = datetime.now() + timedelta(seconds=settings.FOLLOW_UP_DELAY_SECONDS)
        scheduler.add_job(
            send_follow_up,
            "date",
            run_date=run_time,
            args=[user_id, f"🔔 *CommitGuard Alert:* Checking in on commitment: {commitment}", slack_id],
        )
        logger.info("follow_up_scheduled", user_id=user_id, time=run_time.isoformat())

    logger.info("processing_commitment_eval", user_id=user_id, status="completed")


async def startup(_ctx):
    """
    Worker lifecycle management: Initialization.
    """
    logger.info("worker_startup", status="starting_sidecar_scheduler")
    await init_db()
    scheduler.start()


async def shutdown(_ctx):
    """
    Worker lifecycle management: Graceful shutdown.
    """
    logger.info("worker_shutdown", status="stopping_scheduler")
    scheduler.shutdown()


class WorkerSettings:
    """
    ARQ specific configuration for the background worker process.
    """

    functions = [process_commitment_eval]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
