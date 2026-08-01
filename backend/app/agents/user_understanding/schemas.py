from pydantic import BaseModel, Field
from typing import Optional

class UserOnboardingInput(BaseModel):
    goal: str = Field(min_length=1, max_length=200, description="Target career goal or role")
    target_role: Optional[str] = Field(default=None, max_length=200)
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    experience: Optional[str] = Field(default="Intermediate")
    learning_style: Optional[str] = Field(default="Hands-on projects")
    career_stage: Optional[str] = Field(default="Mid-Level")
    available_time: Optional[str] = Field(default="10-15 hours/week")
    preferred_content: list[str] = Field(default_factory=list)
    language: Optional[str] = Field(default="English")

class IdentityTwinAnalysisOutput(BaseModel):
    identity_score: float = Field(ge=0.0, le=100.0)
    identity_drift_percentage: float = Field(ge=0.0, le=100.0)
    key_strengths: list[str]
    skill_gaps: list[str]
    strategic_insight: str
    degraded: bool = False
    reason: Optional[str] = None
