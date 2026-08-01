from pydantic import BaseModel, Field
from typing import List, Optional

class ReflectionCreate(BaseModel):
    reflection: Optional[str] = None
    notes: Optional[str] = None
    mood: Optional[int] = 4
    mood_score: Optional[int] = 4
    motivation: Optional[int] = 4
    energy_level: Optional[int] = 4
    study_hours: Optional[float] = 2.0
    completed_tasks: List[str] = Field(default_factory=list)
    skipped_tasks: List[str] = Field(default_factory=list)
    wins: Optional[str] = ""
    challenges: Optional[str] = ""
    timestamp: Optional[str] = None

class ReflectionResponse(ReflectionCreate):
    id: str
    user_id: str
    risk_level: Optional[str] = "LOW"
    ai_insight: Optional[str] = None
    created_at: str
