"""Pydantic schemas for Reflection Agent."""
from pydantic import BaseModel, Field
from typing import Optional


class ReflectionInput(BaseModel):
    user_id: str = Field(default="", description="User identifier")
    reflection: Optional[str] = None
    notes: Optional[str] = None
    mood: Optional[int] = 4
    mood_score: Optional[int] = 4
    motivation: Optional[int] = 4
    energy_level: Optional[int] = 4
    study_hours: Optional[float] = 2.0
    completed_tasks: list[str] = Field(default_factory=list)
    skipped_tasks: list[str] = Field(default_factory=list)
    wins: Optional[str] = ""
    challenges: Optional[str] = ""
    timestamp: Optional[str] = None


class ReflectionOutput(ReflectionInput):
    id: str
    risk_level: str = "LOW"
    burnout_risk_score: float = 0.0
    ai_insight: str = ""
    created_at: str
