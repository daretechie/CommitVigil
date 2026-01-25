from enum import Enum

from pydantic import BaseModel, Field


class SlippageStatus(str, Enum):
    ON_TRACK = "on_track"
    SLIPPING = "slipping"
    BROKEN = "broken"
    SHADOW_DEBT = "shadow_debt"


class SlippageAnalysis(BaseModel):
    status: SlippageStatus
    fulfillment_ratio: float = Field(..., ge=0, le=1)
    detected_gap: str = Field(..., description="Description of promised vs reality.")
    risk_to_system_stability: float = Field(..., ge=0, le=1)
    intervention_required: bool


class TruthGapAnalysis(BaseModel):
    gap_detected: bool
    truth_score: float = Field(
        ..., ge=0, le=1, description="1.0 means perfect alignment."
    )
    explanation: str
    recommended_tone: str


class GitCommitPromise(BaseModel):
    commit_hash: str
    author_email: str
    message: str
    extracted_tasks: list[str]
    deadline_hint: str | None = None


class GitInbound(BaseModel):
    repository: str
    branch: str
    commits: list[GitCommitPromise]
