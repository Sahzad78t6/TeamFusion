from pydantic import BaseModel, Field
from typing import Optional

class NotificationInput(BaseModel):
    user_id: str = Field(min_length=1)
    streak: Optional[int] = Field(default=1, ge=0)
    latest_task: Optional[str] = Field(default="")
    risk_level: Optional[str] = Field(default="low")
    opportunity_title: Optional[str] = Field(default="")

class NotificationItemSchema(BaseModel):
    id: str
    user_id: str
    title: str = Field(min_length=1)
    message: str = Field(min_length=1)
    type: str
    read: bool = False
    created_at: str

class NotificationOutput(BaseModel):
    notifications: list[NotificationItemSchema]
    degraded: bool = False
    reason: Optional[str] = None
