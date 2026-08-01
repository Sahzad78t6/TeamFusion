from pydantic import BaseModel
from typing import Optional

class ReflectionCreate(BaseModel):
    mood_score: int  # 1 to 5
    energy_level: int # 1 to 5
    notes: str
    wins: str
    challenges: str

class ReflectionResponse(ReflectionCreate):
    id: str
    user_id: str
    ai_insight: Optional[str] = None
    created_at: str
