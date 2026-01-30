# Copyright (c) 2026 CommitVigil AI. All rights reserved.
import json
from datetime import datetime, timedelta, timezone


from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, select

from src.core.config import settings
from src.core.logging import logger
from src.core.state import state
from src.schemas.agents import UserHistory, SafetyRule, CulturalPersona



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
    Gated: Only runs create_all in DEMO_MODE to protect production data.
    """
    if not settings.DEMO_MODE:
        logger.info("db_init_skipped", reason="Not in DEMO_MODE. Use Alembic for production migrations.")
        return

    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
            logger.warning("schema_created_via_code", message="Do not use create_all in production. Use Alembic migrations.")
        logger.info("database_initialized", url=settings.DATABASE_URL)
        await seed_safety_rules()

    except Exception as e:
        logger.warning("database_initialization_warning", error=str(e))


async def get_user_history(user_id: str) -> UserHistory | None:
    """
    Fetch the full UserHistory record for a specific user.
    """
    async with AsyncSessionLocal() as session:
        statement = select(UserHistory).where(UserHistory.user_id == user_id)
        results = await session.execute(statement)
        return results.scalar_one_or_none()


async def get_user_reliability(user_id: str) -> tuple[float, str | None, int]:

    """
    Fetch the reliability score, slack_id, and consecutive firm interventions.
    """
    async with AsyncSessionLocal() as session:
        statement = select(UserHistory).where(UserHistory.user_id == user_id)
        results = await session.execute(statement)
        user = results.scalar_one_or_none()

        if user:
            return (
                user.reliability_score,
                user.slack_id,
                user.consecutive_firm_interventions,
            )
        return 100.0, None, 0


async def update_user_reliability(
    user_id: str, was_failure: bool, tone_used: str = "supportive"
):
    """
    Update historical stats and track ethical Tone-Damping status.
    Uses 'with_for_update' to ensure atomicity during multi-read-write operations.
    """
    async with AsyncSessionLocal() as session:
        # 1. Lock the row for update to ensure atomicity
        statement = (
            select(UserHistory).where(UserHistory.user_id == user_id).with_for_update()
        )
        results = await session.execute(statement)
        user = results.scalar_one_or_none()

        if not user:
            user = UserHistory(
                user_id=user_id,
                total_commitments=1,
                failed_commitments=1 if was_failure else 0,
            )
            session.add(user)
        else:
            user.total_commitments += 1
            if was_failure:
                user.failed_commitments += 1

        # 1.5 Cooling-off Logic: Reset strict intervention counter if enough time has passed
        if user.last_intervention_at:
            last_int = user.last_intervention_at
            # Ensure comparison is timezone-aware
            if last_int.tzinfo is None:
                last_int = last_int.replace(tzinfo=timezone.utc)

            time_since_last = datetime.now(timezone.utc) - last_int
            if time_since_last > timedelta(hours=settings.COOLING_OFF_PERIOD_HOURS):
                user.consecutive_firm_interventions = 0
                logger.info("cooling_off_reset", user_id=user_id, reason="time_elapsed")

        # 2. Ethical Counter Management
        if tone_used in ["firm", "confrontational"]:
            user.consecutive_firm_interventions += 1
            user.last_intervention_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            # Cooling-off logic: Reset counter if a supportive/neutral
            # tone is successfully used
            user.consecutive_firm_interventions = 0

        # 3. Calculate new score (Safely handled within the lock)
        if user.total_commitments > 0:
            user.reliability_score = (
                (user.total_commitments - user.failed_commitments) / user.total_commitments
            ) * 100
        else:
            user.reliability_score = 100.0

        await session.commit()
    logger.info(
        "reliability_updated",
        user_id=user_id,
        new_score=user.reliability_score,
        consecutive_strict=user.consecutive_firm_interventions,
    )


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


async def get_user_by_git_email(git_email: str) -> UserHistory | None:
    """
    Look up a UserHistory record by Git email.
    """
    async with AsyncSessionLocal() as session:
        statement = select(UserHistory).where(UserHistory.git_email == git_email)
        results = await session.execute(statement)
        return results.scalar_one_or_none()
async def get_safety_rules(industry: str = "generic", department: str = "*") -> SafetyRule | None:
    """
    Fetch the safety rules for a specific industry and department with Redis caching.
    Hierarchy: 
    1. Specific Industry + Specific Department
    2. Specific Industry + Wildcard Department (*)
    3. Generic Industry + Wildcard Department (*)
    """
    # Normalize inputs
    industry = industry.lower()
    department = department.lower()
    
    cache_key = f"safety_rules:{industry}:{department}"
    redis = state.get("redis")

    # 1. Check Cache
    if redis:
        try:
            cached = await redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                return SafetyRule(**data)
        except Exception as e:
            logger.warning("cache_lookup_failed", error=str(e))

    # 2. Check Database (Hierarchical)
    async with AsyncSessionLocal() as session:
        # Try specific industry + specific department
        statement = select(SafetyRule).where(
            SafetyRule.industry == industry, 
            SafetyRule.department == department,
            SafetyRule.is_active == True
        )
        results = await session.execute(statement)
        rule = results.scalar_one_or_none()
        
        # Fallback to industry-wide rule
        if not rule and department != "*":
            statement = select(SafetyRule).where(
                SafetyRule.industry == industry, 
                SafetyRule.department == "*",
                SafetyRule.is_active == True
            )
            results = await session.execute(statement)
            rule = results.scalar_one_or_none()
            
        # Fallback to generic rule
        if not rule and industry != "generic":
            statement = select(SafetyRule).where(
                SafetyRule.industry == "generic", 
                SafetyRule.department == "*",
                SafetyRule.is_active == True
            )
            results = await session.execute(statement)
            rule = results.scalar_one_or_none()

    # 3. Populate Cache
    if rule and redis:
        try:
            # Cache for 1 hour
            await redis.setex(cache_key, 3600, rule.model_dump_json())
        except Exception as e:
            logger.warning("cache_population_failed", error=str(e))

    return rule




async def seed_safety_rules():
    """
    Seed the database with initial industry safety rules if they don't exist.
    """
    initial_rules = [
        {
            "industry": "healthcare",
            "hr_keywords": ["HIPAA", "patient data", "medical records", "PHI", "PII"],
            "semantic_rules": "Redact any patient identifiers. Block messages mentioning medical charts or specific treatments.",
        },
        {
            "industry": "finance",
            "hr_keywords": ["insider trading", "SEC compliance", "FINRA", "market manipulation"],
            "semantic_rules": "Block any phrasing that could be interpreted as financial advice or market manipulation.",
        },
        {
            "industry": "legal",
            "hr_keywords": ["privileged", "client-attorney", "deposition", "litigation", "case #"],
            "semantic_rules": "Redact case numbers and specific client names. Ensure no breach of attorney-client privilege in summary.",
        },
        {
            "industry": "generic",
            "hr_keywords": ["Salary", "PIP", "Firing", "Legal Threats"],
            "semantic_rules": "Enforce standard professional conduct and HR boundaries.",
        }
    ]

    async with AsyncSessionLocal() as session:
        for rule_data in initial_rules:
            statement = select(SafetyRule).where(
                SafetyRule.industry == rule_data["industry"],
                SafetyRule.department == "*"
            )
            results = await session.execute(statement)
            if not results.scalar_one_or_none():
                rule = SafetyRule(**rule_data, department="*")
                session.add(rule)
        await session.commit()

    logger.info("safety_rules_seeded")


async def set_safety_rule(
    industry: str, hr_keywords: list[str], semantic_rules: str, department: str = "*", is_active: bool = True, is_verified: bool = False, onboarded_by: str = "system"
) -> SafetyRule:
    """
    Update or create a safety rule for an industry/department and clear its cache.
    """
    industry = industry.lower()
    department = department.lower()

    async with AsyncSessionLocal() as session:
        statement = select(SafetyRule).where(
            SafetyRule.industry == industry,
            SafetyRule.department == department
        )
        results = await session.execute(statement)
        rule = results.scalar_one_or_none()

        if not rule:
            rule = SafetyRule(
                industry=industry,
                department=department,
                hr_keywords=hr_keywords,
                semantic_rules=semantic_rules,
                is_active=is_active,
                is_verified=is_verified,
                onboarded_by=onboarded_by,
            )
            session.add(rule)
        else:
            rule.hr_keywords = hr_keywords
            rule.semantic_rules = semantic_rules
            rule.is_active = is_active
            rule.is_verified = is_verified
            rule.onboarded_by = onboarded_by
            rule.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await session.commit()
        await session.refresh(rule)


    # Cache Invalidation
    redis = state.get("redis")
    if redis:
        try:
            cache_key = f"safety_rules:{industry}:{department}"
            await redis.delete(cache_key)
            logger.info("safety_rule_cache_invalidated", industry=industry, department=department)
        except Exception as e:
            logger.warning("cache_invalidation_failed", error=str(e))

    logger.info("safety_rule_updated", industry=industry, department=department)
    return rule



async def get_cultural_persona(code: str) -> CulturalPersona | None:
    """
    Fetch a cultural persona by code with Redis caching.
    """
    code = code.lower()
    cache_key = f"persona:{code}"
    redis = state.get("redis")

    # 1. Check Cache
    if redis:
        try:
            cached = await redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                return CulturalPersona(**data)
        except Exception as e:
            logger.warning("cache_lookup_failed", error=str(e))

    # 2. Check Database
    async with AsyncSessionLocal() as session:
        statement = select(CulturalPersona).where(CulturalPersona.code == code)
        results = await session.execute(statement)
        persona = results.scalar_one_or_none()

    # 3. Populate Cache
    if persona and redis:
        try:
            await redis.setex(cache_key, 3600, persona.model_dump_json())
        except Exception as e:
            logger.warning("cache_population_failed", error=str(e))

    return persona


async def create_cultural_persona(persona: CulturalPersona) -> CulturalPersona:
    """
    Create or update a cultural persona and invalidate cache.
    """
    persona.code = persona.code.lower()
    async with AsyncSessionLocal() as session:
        session.add(persona)
        await session.commit()
        await session.refresh(persona)

    # Invalidate Cache
    redis = state.get("redis")
    if redis:
        try:
            cache_key = f"persona:{persona.code}"
            await redis.delete(cache_key)
        except Exception as e:
            logger.warning("cache_invalidation_failed", error=str(e))
    
    logger.info("cultural_persona_created", code=persona.code, source=persona.source)
    return persona


async def seed_cultural_personas():
    """
    Seed valid system personas from the static definition in src.core.persona.
    """
    from src.core.persona import CULTURAL_PROMPTS
    
    async with AsyncSessionLocal() as session:
        for code, instruction in CULTURAL_PROMPTS.items():
            code = code.lower()
            statement = select(CulturalPersona).where(CulturalPersona.code == code)
            results = await session.execute(statement)
            if not results.scalar_one_or_none():
                # Derive a simple name from the code or instruction for seeding
                name = f"Standard {code.upper()} Persona"
                if "Japanese" in instruction: name = "Japanese (Wa)"
                elif "German" in instruction: name = "German (Sachlichkeit)"
                elif "Brazilian" in instruction: name = "Brazilian (Jeitinho)"
                
                persona = CulturalPersona(
                    code=code,
                    name=name,
                    instruction=instruction,
                    is_verified=True,
                    source="system"
                )
                session.add(persona)
        await session.commit()
    logger.info("cultural_personas_seeded")
