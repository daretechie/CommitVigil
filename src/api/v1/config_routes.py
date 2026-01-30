# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from fastapi import APIRouter, Depends

from src.api.deps import get_api_key
from src.core.database import set_git_email, set_slack_id, set_safety_rule
from src.schemas.agents import SafetyRule


router = APIRouter()


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


@router.post("/config/safety", dependencies=[Depends(get_api_key)])
async def update_safety_rules(industry: str, hr_keywords: list[str], semantic_rules: str, is_active: bool = True):
    """
    Elite Management: Update safety rules for a specific industry dynamically.
    """
    rule = await set_safety_rule(industry, hr_keywords, semantic_rules, is_active)
    return {"status": "success", "industry": industry, "updated_at": rule.updated_at}

