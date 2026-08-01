from pydantic import BaseModel
from typing import List, Optional

class RecommendationItem(BaseModel):
    id: str
    title: str
    type: str  # course, article, project, book
    provider: Optional[str] = None
    url: Optional[str] = None
    match_score: float = 0.95
    tags: List[str] = []
    author: Optional[str] = None
    duration: Optional[str] = None
    rating: Optional[float] = None
    progress_percentage: Optional[int] = None
    image_url: Optional[str] = None

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[RecommendationItem]
    generated_at: str
