from pydantic import BaseModel, Field
from typing import Optional

class OpportunityInput(BaseModel):
    role: str = Field(min_length=1, max_length=200)
    user_skills: Optional[list[str]] = Field(default_factory=list)
    goal: Optional[str] = Field(default="")
    experience: Optional[str] = Field(default="Intermediate")

class OpportunityItemSchema(BaseModel):
    id: str
    title: str = Field(min_length=1)
    company: str
    location: str
    type: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    description: str
    url: str

class OpportunityMatchOutput(BaseModel):
    opportunities: list[OpportunityItemSchema]
    degraded: bool = False
    reason: Optional[str] = None
