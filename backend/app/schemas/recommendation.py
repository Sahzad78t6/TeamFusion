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

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[RecommendationItem]
    generated_at: str
