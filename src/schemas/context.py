# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from enum import Enum

from pydantic import BaseModel, Field


class IndustryType(str, Enum):
    GENERIC = "generic"
    TECH = "tech"
    HR = "hr"
    FINANCE = "finance"
    LEGAL = "legal"
    REAL_ESTATE = "real_estate"
    ECOMMERCE = "ecommerce"
    HEALTHCARE = "healthcare"
    RESEARCH = "research"


class DepartmentType(str, Enum):
    ENGINEERING = "engineering"
    HR = "hr"
    SALES = "sales"
    LEGAL = "legal"
    FINANCE = "finance"
    OPERATIONS = "operations"
    MARKETING = "marketing"
    GENERIC = "generic"


class CulturalContext(str, Enum):
    HIGH_CONTEXT = "high_context"  # Indirect, relationship-based
    LOW_CONTEXT = "low_context"  # Direct, task-oriented
    BALANCED = "balanced"


class FormalityLevel(str, Enum):
    FORMAL = "formal"
    INFORMAL = "informal"
    CASUAL = "casual"


class DynamicSafetyRule(BaseModel):
    """
    Safety rule generated or selected based on detected industry.
    """

    rule_name: str
    target_tokens: list[str]
    action: str = "redact"  # or "block"
    reasoning: str


class ContextProfile(BaseModel):
    """
    Forensic Context Profile: Automatically detected by the ContextScout.
    """

    industry: str = Field(default="generic")
    department: str = Field(default="*", description="Department-level context.")
    confidence: float = Field(
        default=1.0, description="Confidence level of the context sensing (0.0 to 1.0)."
    )
    culture: CulturalContext = Field(default=CulturalContext.LOW_CONTEXT)

    formality: FormalityLevel = Field(default=FormalityLevel.INFORMAL)
    urgency_level: float = Field(default=0.5, description="0.0 to 1.0 urgency score")
    key_entities: list[str] = Field(
        default_factory=list, description="Industry-specific keywords detected"
    )
    dynamic_safety_rules: list[DynamicSafetyRule] = Field(
        default_factory=list, description="Firewall rules generated for this context"
    )

    reasoning: str = Field(..., description="LLM reasoning for this context detection")
