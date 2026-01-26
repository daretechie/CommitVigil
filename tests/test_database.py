import pytest

from src.core.database import (
    get_user_by_git_email,
    get_user_reliability,
    init_db,
    set_git_email,
    set_slack_id,
    update_user_reliability,
)

# Using shared setup_test_db fixture from conftest.py


@pytest.mark.asyncio
async def test_database_init():
    await init_db()


@pytest.mark.asyncio
async def test_user_reliability_flow():
    user_id = "u1"

    # 1. Initial
    score, _slack_id, consecutive_firm = await get_user_reliability(user_id)
    assert score == 100.0

    # 2. Add as new user with failure (covers line 56)
    await update_user_reliability(user_id, was_failure=True, tone_used="firm")
    score, _, consecutive_firm = await get_user_reliability(user_id)
    assert score == 0.0
    assert consecutive_firm == 1

    # 3. Success for existing user (covers line 60)
    await update_user_reliability(user_id, was_failure=False, tone_used="supportive")
    score, _, consecutive_firm = await get_user_reliability(user_id)
    assert score == 50.0
    assert consecutive_firm == 0

    # 4. Failure for existing user (covers line 62)
    await update_user_reliability(user_id, was_failure=True, tone_used="firm")
    score, _, _ = await get_user_reliability(user_id)
    # 2 failures, 1 success -> 1/3 * 100 = 33.33
    assert 33.3 <= score <= 33.4


@pytest.mark.asyncio
async def test_set_slack_id():
    user_id = "u1"
    # Set for new user
    await set_slack_id(user_id, "s1")
    _, s_id, _ = await get_user_reliability(user_id)
    assert s_id == "s1"

    # Update existing
    await set_slack_id(user_id, "s2")
    _, s_id, _ = await get_user_reliability(user_id)
    assert s_id == "s2"


@pytest.mark.asyncio
async def test_git_email_flow():
    user_id = "u1"
    email = "test@example.com"

    # Set for new user
    await set_git_email(user_id, email)
    user = await get_user_by_git_email(email)
    assert user.user_id == user_id
    assert user.git_email == email

    # Update existing
    await set_git_email(user_id, "other@example.com")
    user = await get_user_by_git_email("other@example.com")
    assert user.git_email == "other@example.com"

    # Get non-existent
    user = await get_user_by_git_email("nonexistent@example.com")
    assert user is None
