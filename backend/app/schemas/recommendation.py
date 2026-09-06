from pydantic import BaseModel, Field
from typing import List, Optional

class RecommendationItem(BaseModel):
    id: str
    title: str
    type: str = "course"  # course, article, project, book, video
    provider: Optional[str] = "GrowthOS AI Curator"
    channel: Optional[str] = None
    url: Optional[str] = None
    link: Optional[str] = None
    match_score: Optional[float] = 92.0
    matchScore: Optional[float] = 92.0
    tags: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    duration: Optional[str] = "20 Mins"
    difficulty: Optional[str] = "Intermediate"
    rating: Optional[float] = 4.9
    progress_percentage: Optional[int] = 0
    progressPercentage: Optional[int] = 0
    image_url: Optional[str] = None
    imageUrl: Optional[str] = None
    thumbnail: Optional[str] = None
    why_recommended: Optional[str] = None
    reason: Optional[str] = None
    source: Optional[str] = "youtube"
    created_at: Optional[str] = None

    class Config:
        extra = "allow"

class RefreshRecommendationRequest(BaseModel):
    topic: Optional[str] = None
    target_role: Optional[str] = None

    class Config:
        extra = "allow"

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    resources: List[RecommendationItem] = Field(default_factory=list)
    generated_at: Optional[str] = None
    target_role: Optional[str] = None
    ai_feedback: Optional[str] = None

    class Config:
        extra = "allow"
