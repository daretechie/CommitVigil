from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import select, SQLModel
from src.core.config import settings
from src.core.logging import logger
from src.schemas.agents import UserHistory

# Async Engine for PostgreSQL
engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

# Async Session Factory (Singleton-like)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def init_db():
    """
    Initialize the database and create tables using SQLModel.
    """
    async with engine.begin() as conn:
        # In a real enterprise app, we'd use Alembic migrations.
        # For this portfolio build, we'll use create_all for speed.
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("database_initialized", url=settings.DATABASE_URL)

async def get_user_reliability(user_id: str) -> tuple[float, str | None, int]:
    """
    Fetch the reliability score, slack_id, and consecutive firm intervetions.
    """
    async with AsyncSessionLocal() as session:
        statement = select(UserHistory).where(UserHistory.user_id == user_id)
        results = await session.execute(statement)
        user = results.scalar_one_or_none()
        
        if user:
            return user.reliability_score, user.slack_id, user.consecutive_firm_interventions
        return 100.0, None, 0


async def update_user_reliability(user_id: str, was_failure: bool, tone_used: str = "supportive"):
    """
    Update historical stats and track ethical Tone-Damping status.
    """
    async with AsyncSessionLocal() as session:
        statement = select(UserHistory).where(UserHistory.user_id == user_id)
        results = await session.execute(statement)
        user = results.scalar_one_or_none()

        if not user:
            user = UserHistory(
                user_id=user_id,
                total_commitments=1,
                failed_commitments=1 if was_failure else 0
            )
            session.add(user)
        else:
            user.total_commitments += 1
            if was_failure:
                user.failed_commitments += 1
        
        # Ethical Counter Management
        if tone_used in ["firm", "confrontational"]:
            user.consecutive_firm_interventions += 1
            user.last_intervention_at = datetime.now().isoformat()
        else:
            # Cooling-off logic: Reset counter if a supportive/neutral tone is successfuly used
            user.consecutive_firm_interventions = 0
        
        # Calculate new score
        user.reliability_score = ((user.total_commitments - user.failed_commitments) / user.total_commitments) * 100
        
        await session.commit()
    logger.info("reliability_updated", user_id=user_id, new_score=user.reliability_score, consecutive_strict=user.consecutive_firm_interventions)


async def set_slack_id(user_id: str, slack_id: str):
    """
    Maps an internal user_id to a Slack Member ID using SQLModel.
    """
    async with AsyncSessionLocal() as session:
        statement = select(UserHistory).where(UserHistory.user_id == user_id)
        results = await session.execute(statement)
        user = results.scalar_one_or_none()

        if not user:
            user = UserHistory(user_id=user_id, slack_id=slack_id)
            session.add(user)
        else:
            user.slack_id = slack_id
            
        await session.commit()
    logger.info("slack_id_mapped", user_id=user_id, slack_id=slack_id)

async def set_git_email(user_id: str, git_email: str):
    """
    Maps an internal user_id to a Git Email using SQLModel.
    """
    async with AsyncSessionLocal() as session:
        statement = select(UserHistory).where(UserHistory.user_id == user_id)
        results = await session.execute(statement)
        user = results.scalar_one_or_none()

        if not user:
            user = UserHistory(user_id=user_id, git_email=git_email)
            session.add(user)
        else:
            user.git_email = git_email
            
        await session.commit()
    logger.info("git_email_mapped", user_id=user_id, git_email=git_email)

async def get_user_by_git_email(git_email: str) -> Optional[UserHistory]:
    """
    Look up a UserHistory record by Git email.
    """
    async with AsyncSessionLocal() as session:
        statement = select(UserHistory).where(UserHistory.git_email == git_email)
        results = await session.execute(statement)
        return results.scalar_one_or_none()

