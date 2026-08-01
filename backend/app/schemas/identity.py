from pydantic import BaseModel
from typing import List, Optional

class IdentityBase(BaseModel):
    current_role: str
    target_role: str
    skills: List[str] = []
    career_goals: List[str] = []
    learning_style: Optional[str] = "visual"

class IdentityCreate(IdentityBase):
    pass

class IdentityResponse(IdentityBase):
    id: str
    user_id: str
    updated_at: str
