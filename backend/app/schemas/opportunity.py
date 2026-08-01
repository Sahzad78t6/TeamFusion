from pydantic import BaseModel
from typing import List, Optional

class OpportunityItem(BaseModel):
    id: str
    title: str
    company: str
    location: str
    type: str  # job, internship, hackathon, grant
    relevance_score: float
    description: str
    url: Optional[str] = None

class OpportunityResponse(BaseModel):
    user_id: str
    opportunities: List[OpportunityItem]
    updated_at: str
