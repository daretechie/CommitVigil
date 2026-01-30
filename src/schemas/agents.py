# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel



class ExcuseCategory(str, Enum):
    LEGITIMATE = "legitimate"  # e.g., Family emergency, health
    DEFLECTION = "deflection"  # e.g., "I forgot," "Too busy"
    BURNOUT_SIGNAL = "burnout_signal"  # e.g., Extreme fatigue, losing interest


class ExcuseAnalysis(BaseModel):
    category: ExcuseCategory
    confidence_score: float = Field(..., ge=0, le=1)
    reasoning: str = Field(..., description="The logic behind the classification.")


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAssessment(BaseModel):
    risk_score: float = Field(..., ge=0, le=1)
    level: RiskLevel
    predicted_latency_days: int = Field(
        ..., description="Estimated delay in completion."
    )
    mitigation_strategy: str


class BurnoutDetection(BaseModel):
    is_at_risk: bool
    sentiment_indicators: list[str]
    recommendation: str


class ToneType(str, Enum):
    SUPPORTIVE = "supportive"
    NEUTRAL = "neutral"
    FIRM = "firm"
    CONFRONTATIONAL = "confrontational"


class AgentDecision(BaseModel):
    action: str
    tone: ToneType
    message: str
    analysis_summary: str


class SafetyAudit(BaseModel):
    is_safe: bool
    requires_human_review: bool = False
    is_hard_blocked: bool = False  # For HR/Legal territory
    risk_of_morale_damage: float = Field(..., ge=0, le=1)
    supervisor_confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence in the audit verdict.",
    )
    suggested_correction: str | None = None
    correction_type: str = Field(
        default="none", description="'none', 'surgical', 'full_rewrite'"
    )
    reasoning: str


class SafetyIntervention(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))  # UUID for feedback correlation
    original_message: str
    corrected_message: str | None
    reasoning: str
    intervention_type: str  # 'correction', 'block', 'review'


class PipelineEvaluation(BaseModel):
    decision: AgentDecision
    excuse: ExcuseAnalysis
    risk: RiskAssessment
    burnout: BurnoutDetection
    safety_audit: SafetyIntervention | None = None


class ExtractedCommitment(BaseModel):
    task: str = Field(..., description="The task the user committed to.")
    deadline: str = Field(
        ..., description="The deadline extracted (e.g., Friday 5 PM)."
    )
    confidence_score: float = Field(..., ge=0, le=1)


class SlackCommitmentRecord(BaseModel):
    commitment_found: bool = Field(
        ..., description="True if a promise was actually found."
    )
    who: str | None = Field(
        default=None, description="The person who made the promise."
    )
    what: str | None = Field(default=None, description="The action or task promised.")
    when: str | None = Field(
        default=None, description="The deadline or time frame promised."
    )


class CommitmentUpdate(BaseModel):
    user_id: str
    commitment: str
    check_in: str
    industry: str = "generic"  # Use "AUTO" for dynamic sensing


class UserHistory(SQLModel, table=True):
    __tablename__ = "user_history"

    user_id: str = Field(primary_key=True, index=True)
    slack_id: str | None = Field(default=None, index=True)
    git_email: str | None = Field(default=None, index=True)
    total_commitments: int = Field(default=0)
    failed_commitments: int = Field(default=0)
    reliability_score: float = Field(default=100.0)

    # Enterprise Attributes
    department: str = Field(
        default="engineering", index=True
    )  # engineering, hr, research, finance
    industry_type: str = Field(default="generic")  # healthcare, finance, generic
    is_context_verified: bool = Field(default=False, description="Whether the industry/department has been confirmed for this user.")
    language_preference: str = Field(default="en")  # en, en-UK, ja, de


    # Ethical Tracking
    consecutive_firm_interventions: int = Field(default=0)
    last_intervention_at: datetime | None = Field(default=None)


class AggregateReport(BaseModel):
    department: str
    total_members: int
    average_reliability_score: float
    burnout_risk_count: int
    top_performers: list[str]
    critical_risk_members: list[str]
    intervention_acceptance_rate: float
    strategy_recommendation: str | None = None


class ROIPrediction(BaseModel):
    """
    Sales Intelligence: Predicts potential savings for a prospect.
    """
    annual_savings_usd: float
    developer_hours_recovered: float
    slippage_reduction_percent: float
    payback_period_months: float
    calculation_basis: str


class ProspectProfile(BaseModel):
    """
    Sales Intelligence: Input for generating high-impact demo audits.
    """
    company_name: str
    target_role: str  # e.g., CTO, VP Engineering
    team_size: int
    avg_developer_salary: float = Field(default=150000.0)
    drift_scenarios: list[dict[str, str]] = Field(
        default_factory=list,
        description="Fictional scenarios: {'who': 'Dev A', 'promise': '...', 'reality': '...'}"
    )



class SafetyFeedback(SQLModel, table=True):
    """
    Continuous Learning: Persists manager overrides for model tuning.
    """

    __tablename__ = "safety_feedback"

    id: int | None = Field(default=None, primary_key=True)
    intervention_id: str = Field(index=True)
    manager_id: str
    user_id: str = Field(index=True)
    action_taken: str  # accepted, rejected, modified
    final_message_sent: str
    feedback_notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


class ReportSummary(BaseModel):
    report_id: str
    generated_at: str
    subject: dict[str, Any]
    performance_metrics: dict[str, Any]
    integrity_score: dict[str, Any]
    intervention_recommendation: dict[str, Any]
    commitments: list[str] = []
    reality: str = ""


class CorrectionFeedback(BaseModel):
    intervention_id: str
    user_id: str = Field(
        ..., description="The ID of the user whose commitment was corrected."
    )
    manager_id: str
    action_taken: str = Field(..., description="'accepted', 'rejected', 'modified'")
    final_message_sent: str
    comments: str | None = None


class LanguageResponse(BaseModel):
    code: str


class SafetyRule(SQLModel, table=True):
    """
    Enterprise Safety Layer: Dynamic industry and department specific rules.
    """

    __tablename__ = "safety_rules"

    id: int | None = Field(default=None, primary_key=True)
    industry: str = Field(index=True)
    department: str = Field(default="*", index=True) # "*" acts as a wildcard for all departments in an industry
    hr_keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON)) 
    semantic_rules: str
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False, description="Whether this rule has been approved by a manager.")
    onboarded_by: str = Field(default="system", description="Source of the rule (system/manager/manual).")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


class CulturalPersona(SQLModel, table=True):
    """
    Adaptive Persona System: Dynamic cultural communication styles.
    """
    __tablename__ = "cultural_personas"

    code: str = Field(primary_key=True, index=True)  # e.g., "it", "ko"
    name: str  # e.g., "Italian Professional"
    instruction: str  # The prompt definition
    is_verified: bool = Field(default=False)  # HITL flag
    source: str = Field(default="auto_generated")  # "system" or "auto_generated"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
