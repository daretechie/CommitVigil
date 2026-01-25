from enum import Enum

from pydantic import BaseModel
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


class SafetyIntervention(BaseModel):
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
    who: str = Field(..., description="The person who made the promise.")
    what: str = Field(..., description="The action or task promised.")
    when: str = Field(..., description="The deadline or time frame promised.")


class CommitmentUpdate(BaseModel):
    user_id: str
    commitment: str
    check_in: str


class UserHistory(SQLModel, table=True):
    __tablename__ = "user_history"

    user_id: str = Field(primary_key=True, index=True)
    slack_id: str | None = Field(default=None)
    git_email: str | None = Field(default=None)
    total_commitments: int = Field(default=0)
    failed_commitments: int = Field(default=0)
    reliability_score: float = Field(default=100.0)

    # Ethical Tracking
    consecutive_firm_interventions: int = Field(default=0)
    last_intervention_at: str | None = Field(default=None)
