"""Pydantic schemas for User Understanding Agent."""
from pydantic import BaseModel, Field
from typing import Optional


class UserUnderstandingInput(BaseModel):
    user_id: str = Field(default="", description="User identifier")
    goal: str = Field(default="", max_length=200, description="Target career goal or role")
    target_role: Optional[str] = Field(default=None, max_length=200)
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    experience: Optional[str] = Field(default="Intermediate")
    learning_style: Optional[str] = Field(default="Hands-on projects")
    career_stage: Optional[str] = Field(default="Mid-Level")
    available_time: Optional[str] = Field(default="10-15 hours/week")
    preferred_content: list[str] = Field(default_factory=list)
    language: Optional[str] = Field(default="English")


class UserUnderstandingOutput(BaseModel):
    target_role: str
    skills: list[str]
    interests: list[str]
    learning_style: str = "hands-on"
    available_time_per_week_hours: int = 5
    aspirations: str = ""
    identity_score: float = Field(ge=0.0, le=100.0, default=85.0)
    identity_drift_percentage: float = Field(ge=0.0, le=100.0, default=12.0)
    key_strengths: list[str] = Field(default_factory=list)
    skill_gaps: list[str] = Field(default_factory=list)
    strategic_insight: Optional[str] = None
