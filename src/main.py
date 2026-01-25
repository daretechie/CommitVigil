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
async def lifespan(fastapi_app: FastAPI):
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

@app.post("/users/config/git")
async def map_git_user(user_id: str, git_email: str):
    """
    Elite Config Feature: Map an internal user reference to a Git Email.
    """
    from src.core.database import set_git_email
    await set_git_email(user_id, git_email)
    return {"status": "success", "message": f"Mapped {user_id} to Git Email {git_email}"}

@app.post("/ingest/git")
async def ingest_git_commitment(commit_data: dict):
    """
    Advanced GitOps Feature: Extract commitments directly from Git Commit Messages.
    """
    from src.agents.commitment_extractor import CommitmentExtractor
    from src.core.database import get_user_by_git_email
    
    extractor = CommitmentExtractor()
    author_email = commit_data.get("author_email")
    message = commit_data.get("message")
    
    user = await get_user_by_git_email(author_email)
    user_id = user.user_id if user else "unknown_git_user"
    
    extracted = await extractor.parse_conversation(message)
    logger.info("git_commitment_extracted", user_id=user_id, task=extracted.what)
    
    return {
        "status": "extracted",
        "owner": extracted.who,
        "task": extracted.what,
        "identity_matched": user_id != "unknown_git_user"
    }

@app.get("/reports/audit/{user_id}")
async def get_performance_audit(user_id: str):
    """
    CASH-GENERATION ENDPOINT: Generates a professional Performance Integrity Audit.
    This is the deliverable you sell to Engineering Managers.
    """
    from src.core.database import get_user_reliability
    from src.agents.performance import SlippageAnalyst, TruthGapDetector
    from src.core.reporting import AuditReportGenerator
    
    # 1. Gather Data
    score, slack_id = await get_user_reliability(user_id)
    # Mocking historical evidence for the audit report demo
    promised = ["Refactor API", "Fix CSS", "Update Docs"]
    reality = "Only updated some typos in README. No major code changes detected."
    
    # 2. Run Agents
    analyst = SlippageAnalyst()
    detector = TruthGapDetector()
    
    slippage = await analyst.analyze_performance_gap(promised, reality)
    gap = await detector.detect_gap("I am 90% done with the refactor", reality)
    
    # 3. Compile Report
    from src.schemas.agents import UserHistory
    user_mock = UserHistory(user_id=user_id, reliability_score=score, total_commitments=10)
    
    report = AuditReportGenerator.generate_audit_summary(user_mock, slippage, gap)
    
    return report

