from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.config import settings
from src.core.database import get_safety_rules, init_db, set_safety_rule, update_user_reliability
from src.llm.factory import LLMFactory
from src.llm.groq import GroqProvider
from src.llm.mock import MockProvider
from src.llm.openai import OpenAIProvider
from src.schemas.agents import SafetyRule, UserHistory


@pytest.mark.asyncio
async def test_llm_factory_steering():
    """Test explicit provider steering in LLMFactory."""
    with patch("src.llm.factory.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = "sk-test"
        mock_settings.GROQ_API_KEY = "gsk-test"

        # Test OpenAI explicit
        provider = LLMFactory.get_provider("openai")
        assert isinstance(provider, OpenAIProvider)

        # Test Groq explicit
        provider = LLMFactory.get_provider("groq")
        assert isinstance(provider, GroqProvider)

        # Test Mock explicit
        provider = LLMFactory.get_provider("mock")
        assert isinstance(provider, MockProvider)


@pytest.mark.asyncio
async def test_llm_factory_auto_detect():
    """Test auto-detection of providers in LLMFactory."""
    # Test OpenAI auto-detect
    with patch("src.llm.factory.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = None
        mock_settings.OPENAI_API_KEY = "sk-test"
        mock_settings.GROQ_API_KEY = None
        provider = LLMFactory.get_provider()
        assert isinstance(provider, OpenAIProvider)

    # Test Groq auto-detect
    with patch("src.llm.factory.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = None
        mock_settings.OPENAI_API_KEY = None
        mock_settings.GROQ_API_KEY = "gsk-test"
        provider = LLMFactory.get_provider()
        assert isinstance(provider, GroqProvider)


@pytest.mark.asyncio
async def test_llm_factory_fallback():
    """Test fallback to mock when no keys are available."""
    with patch("src.llm.factory.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = None
        mock_settings.OPENAI_API_KEY = None
        mock_settings.GROQ_API_KEY = None
        provider = LLMFactory.get_provider()
        assert isinstance(provider, MockProvider)


@pytest.mark.asyncio
async def test_database_cooling_off_reset():
    """Test that the consecutive_firm_interventions counter resets after cooling off."""
    user_id = "test_cooling_user"

    # 1. Setup user in database with last intervention 25 hours ago
    past_time = datetime.now(UTC) - timedelta(hours=settings.COOLING_OFF_PERIOD_HOURS + 1)

    with patch("src.core.database.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_user = UserHistory(
            user_id=user_id,
            reliability_score=80.0,
            consecutive_firm_interventions=3,
            last_intervention_at=past_time,
            total_commitments=10,
            failed_commitments=2,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        # 2. Update reliability with a supportive tone
        await update_user_reliability(user_id, was_failure=False, tone_used="supportive")

        # 3. Assert counter was reset
        assert mock_user.consecutive_firm_interventions == 0


@pytest.mark.asyncio
async def test_database_hierarchical_safety_rules():
    """Test the hierarchical lookup of safety rules."""
    with patch("src.core.database.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        # Case 1: Industry fallback (Engineering/Wildcard -> Engineering/*)
        mock_result = MagicMock()
        # First call (specific) returns None, second call (wildcard) returns a rule
        mock_result.scalar_one_or_none.side_effect = [
            None,
            SafetyRule(industry="engineering", department="*", semantic_rules="test"),
        ]
        mock_session.execute.return_value = mock_result

        rule = await get_safety_rules(industry="engineering", department="dev")
        assert rule.industry == "engineering"
        assert rule.department == "*"

        # Case 2: Generic fallback (Finance/Wildcard -> Generic/*)
        mock_result = MagicMock()
        # specific fails, industry-wide fails, generic succeeds
        mock_result.scalar_one_or_none.side_effect = [
            None,
            None,
            SafetyRule(industry="generic", department="*", semantic_rules="generic test"),
        ]
        mock_session.execute.return_value = mock_result

        rule = await get_safety_rules(industry="finance", department="trading")
        assert rule.industry == "generic"


@pytest.mark.asyncio
async def test_database_redis_cache_logic():
    """Test Redis caching logic in get_safety_rules."""
    from src.core.state import state

    # 1. Test cache hit
    mock_redis = AsyncMock()
    mock_redis.get.return_value = (
        '{"industry": "cached", "department": "*", "semantic_rules": "rules"}'
    )
    state["redis"] = mock_redis

    rule = await get_safety_rules(industry="cached", department="*")
    assert rule.industry == "cached"
    mock_redis.get.assert_called_once()

    # 2. Test cache miss and population
    mock_redis.get.return_value = None
    state["redis"] = mock_redis

    with patch("src.core.database.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = SafetyRule(
            industry="uncached", department="*", semantic_rules="rules"
        )
        mock_session.execute.return_value = mock_result

        rule = await get_safety_rules(industry="uncached", department="*")
        assert rule.industry == "uncached"
        mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_database_init_exception():
    """Test error handling in init_db."""
    with patch("src.core.database.engine") as mock_engine:
        mock_engine.begin.side_effect = Exception("DB Connection Failed")
        # Should not raise, just log warning
        await init_db()


@pytest.mark.asyncio
async def test_set_safety_rule_new_and_update():
    """Test creating and updating safety rules."""
    with patch("src.core.database.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # session.add is synchronous
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        # 1. Update existing rule
        mock_rule = SafetyRule(industry="test", department="*", hr_keywords=[], semantic_rules="")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_rule
        mock_session.execute.return_value = mock_result

        await set_safety_rule("test", ["key"], "new rules")
        assert mock_rule.semantic_rules == "new rules"

        # 2. Create new rule
        mock_result.scalar_one_or_none.return_value = None
        await set_safety_rule("new", ["key"], "new rules")
        # Ensure session.add was called (it shouldn't be a coroutine)
        mock_session.add.assert_called()
