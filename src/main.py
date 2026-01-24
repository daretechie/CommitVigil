from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from prometheus_fastapi_instrumentator import Instrumentator
from src.core.config import settings
from src.core.logging import setup_logging, logger
from src.core.database import init_db, set_slack_id
from src.schemas.agents import CommitmentUpdate


from arq import create_pool
from arq.connections import RedisSettings

# Initialize Logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Modern lifespan management for Enterprise FastAPI apps.
    Handles startup and shutdown logic.
    """
    logger.info("application_startup", status="initializing_resources")
    await init_db()
    yield
    logger.info("application_shutdown", status="cleaning_up")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Instrument for Prometheus Metrics
Instrumentator().instrument(app).expose(app)


@app.get("/health")
async def health_check():
    logger.info("health_check_triggered", status="ok")
    return {"status": "ok", "app": settings.PROJECT_NAME}


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}. Visit /docs for API documentation."
    }


@app.post("/evaluate")
async def evaluate_commitment(update: CommitmentUpdate):
    """
    Main ingestion gateway for commitment evaluations.
    """
    # Connect to Redis
    redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))

    # Offload the Agentic work to the background worker
    await redis.enqueue_job(
        "process_commitment_eval",
        user_id=update.user_id,
        commitment=update.commitment,
        check_in=update.check_in,
    )

    logger.info("commitment_enqueued", user_id=update.user_id)
    return {
        "status": "enqueued",
        "message": "The Accountability Agent is analyzing your update.",
    }


@app.post("/ingest/raw")
async def ingest_raw_commitment(user_id: str, raw_text: str):
    """
    Elite Feature: Extract structured commitment record from raw Slack/Discord text.
    """
    from src.agents.commitment_extractor import CommitmentExtractor

    extractor = CommitmentExtractor()

    extracted = await extractor.parse_conversation(raw_text)

    # Audit: In a full production system, we would persist this to a 'tasks' table.
    logger.info(
        "commitment_extracted",
        user_id=user_id,
        task=extracted.what,
        owner=extracted.who,
    )

    return {
        "status": "extracted",
        "owner": extracted.who,
        "task": extracted.what,
        "deadline": extracted.when,
        "message": f"Successfully parsed promise from {extracted.who}"
    }

@app.post("/users/config/slack")
async def map_slack_user(user_id: str, slack_id: str):
    """
    Elite Config Feature: Map an internal user reference to a Slack Member ID.
    Example: user_id='john_dev' -> slack_id='U12345678'
    """
    await set_slack_id(user_id, slack_id)
    return {"status": "success", "message": f"Mapped {user_id} to Slack ID {slack_id}"}
