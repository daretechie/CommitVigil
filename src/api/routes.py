from typing import cast

from fastapi import APIRouter, Depends
from src.agents.commitment_extractor import CommitmentExtractor
from src.agents.performance import SlippageAnalyst, TruthGapDetector
from src.api.deps import get_api_key
from src.core.database import (
    get_user_by_git_email,
    get_user_reliability,
    set_git_email,
    set_slack_id,
)
from src.core.logging import logger
from src.core.reporting import AuditReportGenerator
from src.schemas.agents import CommitmentUpdate, CorrectionFeedback, UserHistory

# State will be injected or accessed via global state for now (pending further refactor)
from src.core.state import state

router = APIRouter()


@router.post("/evaluate", dependencies=[Depends(get_api_key)])
async def evaluate_commitment(update: CommitmentUpdate):
    """
    Main ingestion gateway for commitment evaluations.
    """
    if not state["redis"]:
        return {"status": "error", "message": "Redis pool not initialized"}

    # Offload the Agentic work to the background worker
    job = await state["redis"].enqueue_job(
        "process_commitment_eval",
        user_id=update.user_id,
        commitment=update.commitment,
        check_in=update.check_in,
    )

    if not job:
        return {"status": "error", "message": "Failed to enqueue job"}

    logger.info("commitment_enqueued", user_id=update.user_id, job_id=job.job_id)
    return {
        "status": "enqueued",
        "job_id": job.job_id,
        "message": "The Accountability Agent is analyzing your update.",
    }


@router.post("/ingest/raw", dependencies=[Depends(get_api_key)])
async def ingest_raw_commitment(user_id: str, raw_text: str):
    """
    Elite Feature: Extract structured commitment record from raw Slack/Discord text.
    """
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
        "message": f"Successfully parsed promise from {extracted.who}",
    }


@router.post("/users/config/slack", dependencies=[Depends(get_api_key)])
async def map_slack_user(user_id: str, slack_id: str):
    """
    Elite Config Feature: Map an internal user reference to a Slack Member ID.
    Example: user_id='john_dev' -> slack_id='U12345678'
    """
    await set_slack_id(user_id, slack_id)
    return {"status": "success", "message": f"Mapped {user_id} to Slack ID {slack_id}"}


@router.post("/users/config/git", dependencies=[Depends(get_api_key)])
async def map_git_user(user_id: str, email: str):
    """
    Elite Config Feature: Map an internal user reference to a Git Email.
    """
    await set_git_email(user_id, email)
    return {
        "status": "success",
        "message": f"Mapped {user_id} to Git Email {email}",
    }


@router.post("/ingest/git", dependencies=[Depends(get_api_key)])
async def ingest_git_commitment(commit_data: dict):
    """
    Advanced GitOps Feature: Extract commitments directly from Git Commit Messages.
    """
    extractor = CommitmentExtractor()
    author_email = commit_data.get("author_email")
    message = commit_data.get("message")

    if not isinstance(author_email, str) or not isinstance(message, str):
        return {
            "status": "error",
            "message": "Invalid input: author_email and message must be strings.",
        }

    # Explicit cast for MyPy (redundant at runtime but needed for strict static analysis)
    safe_email = cast(str, author_email)
    safe_message = cast(str, message)

    user = await get_user_by_git_email(safe_email)
    user_id = user.user_id if user else "unknown_git_user"

    extracted = await extractor.parse_conversation(safe_message)
    logger.info("git_commitment_extracted", user_id=user_id, task=extracted.what)

    return {
        "status": "extracted",
        "owner": extracted.who,
        "task": extracted.what,
        "identity_matched": user_id != "unknown_git_user",
    }


@router.get("/reports/audit/{user_id}", dependencies=[Depends(get_api_key)])
async def get_performance_audit(user_id: str, report_format: str = "json"):
    """
    CASH-GENERATION ENDPOINT: Generates a professional Performance Integrity Audit.
    Supports report_format='json', report_format='markdown', or report_format='html'.
    """
    # 1. Gather Data
    score, _, _ = await get_user_reliability(user_id)

    # Mocking historical evidence for the audit report demo
    promised = ["Refactor API", "Fix CSS", "Update Docs"]
    reality = "Only updated some typos in README. No major code changes detected."

    # 2. Run Agents
    analyst = SlippageAnalyst()
    detector = TruthGapDetector()

    slippage = await analyst.analyze_performance_gap(promised, reality)
    gap = await detector.detect_gap("I am 90% done with the refactor", reality)

    # 3. Compile Report
    user_mock = UserHistory(
        user_id=user_id, reliability_score=score, total_commitments=10
    )

    summary = AuditReportGenerator.generate_audit_summary(user_mock, slippage, gap)

    if report_format == "markdown":
        return {"content": AuditReportGenerator.generate_markdown_audit(summary)}
    elif report_format == "html":
        from fastapi.responses import HTMLResponse

        return HTMLResponse(content=AuditReportGenerator.generate_html_audit(summary))

    return summary


@router.post("/feedback/safety", dependencies=[Depends(get_api_key)])
async def log_safety_feedback(feedback: CorrectionFeedback):
    """
    Priority 1 Feature: Track manager acceptance of Safety Supervisor interventions.
    """
    logger.info(
        "safety_feedback_received",
        intervention_id=feedback.intervention_id,
        action=feedback.action_taken,
        manager=feedback.manager_id,
    )
    return {"status": "logged", "message": "Safety feedback recorded for model tuning."}
