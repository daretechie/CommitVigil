from pydantic import BaseModel, Field
from enum import Enum


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


class GitCommitPromise(BaseModel):
    commit_hash: str
    author_email: str
    message: str
    extracted_tasks: list[str]
    deadline_hint: Optional[str] = None


class GitInbound(BaseModel):
    repository: str
    branch: str
    commits: list[GitCommitPromise]
