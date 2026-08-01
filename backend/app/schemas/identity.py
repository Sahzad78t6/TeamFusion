from pydantic import BaseModel, Field
from typing import List, Optional, Union

class IdentityBase(BaseModel):
    goal: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    experience: Optional[str] = "Intermediate"
    learning_style: Optional[str] = "Hands-on projects"
    career_stage: Optional[str] = "Mid-Level Engineer"
    available_time: Optional[str] = "10-15 hours/week"
    preferred_content: Union[List[str], str] = Field(default_factory=lambda: ["Courses", "Labs"])
    language: Optional[str] = "English"
    current_role: Optional[str] = "Software Engineer"
    target_role: Optional[str] = "AI Engineer"

class IdentityCreate(IdentityBase):
    pass

class IdentityResponse(IdentityBase):
    id: str
    user_id: str
    identity_score: Optional[float] = 88.0
    identity_drift_percentage: Optional[float] = 12.0
    key_strengths: Optional[List[str]] = Field(default_factory=list)
    skill_gaps: Optional[List[str]] = Field(default_factory=list)
    strategic_insight: Optional[str] = None
    updated_at: str
