from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

# Base Schema Model
class MongoBaseModel(BaseModel):
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

# User Model
class UserInDB(MongoBaseModel):
    name: str
    email: str
    password_hash: str
    refresh_token: Optional[str] = None

# Identity Twin Model
class IdentityTwin(MongoBaseModel):
    user_id: str
    traits: Dict[str, Any] = {}
    preferences: Dict[str, Any] = {}
    learning_style: Optional[str] = None

# Recommendation Model
class Recommendation(MongoBaseModel):
    user_id: str
    type: str # e.g. "course", "article", "habit"
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    status: str = "pending" # pending, accepted, rejected

# Reflection Model
class Reflection(MongoBaseModel):
    user_id: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content: str
    sentiment: Optional[str] = None
    tags: List[str] = []

# Planner Model (Learning Plans)
class LearningPlan(MongoBaseModel):
    user_id: str
    goal: str
    milestones: List[Dict[str, Any]] = []
    status: str = "in_progress" # in_progress, completed, abandoned

# Notification Model
class Notification(MongoBaseModel):
    user_id: str
    title: str
    message: str
    is_read: bool = False
    action_url: Optional[str] = None

# Analytics Model
class AnalyticsEvent(MongoBaseModel):
    user_id: str
    event_type: str
    event_data: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
