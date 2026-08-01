from pydantic import BaseModel, Field
from typing import Optional

class LearningCuratorInput(BaseModel):
    target_role: str = Field(min_length=1, max_length=200)
    skills: Optional[list[str]] = Field(default_factory=list)
    learning_style: Optional[str] = Field(default="Interactive")

class ResourceItemSchema(BaseModel):
    id: str
    title: str = Field(min_length=1)
    type: str = Field(pattern="^(course|book|paper|video|article|podcast)$")
    provider: str
    author: str
    duration: str
    rating: float = Field(ge=0.0, le=5.0)
    match_score: float = Field(ge=0.0, le=1.0)
    progress_percentage: int = Field(ge=0, le=100)
    url: str
    image_url: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

class CuratedRecommendationsOutput(BaseModel):
    recommendations: list[ResourceItemSchema]
    degraded: bool = False
    reason: Optional[str] = None
