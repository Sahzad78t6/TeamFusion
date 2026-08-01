from pydantic import BaseModel, Field
from typing import Optional

class ReflectionInput(BaseModel):
    reflection: Optional[str] = None
    notes: Optional[str] = None
    mood: Optional[int] = Field(default=None, ge=1, le=5)
    mood_score: Optional[int] = Field(default=None, ge=1, le=5)
    motivation: Optional[int] = Field(default=None, ge=1, le=5)
    energy_level: Optional[int] = Field(default=None, ge=1, le=5)
    study_hours: Optional[float] = Field(default=2.5, ge=0.0, le=24.0)
    completed_tasks: Optional[list[str]] = Field(default_factory=list)
    skipped_tasks: Optional[list[str]] = Field(default_factory=list)

class ReflectionOutput(BaseModel):
    user_id: str
    reflection: str
    risk_level: str
    ai_insight: str
    degraded: bool = False
    reason: Optional[str] = None
