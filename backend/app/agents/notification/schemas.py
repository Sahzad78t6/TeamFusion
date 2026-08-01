"""Pydantic schemas for Notification Agent."""
from pydantic import BaseModel, Field
from typing import Optional


class NotificationInput(BaseModel):
    user_id: str = Field(default="", description="User identifier")
    event_type: str = Field(default="general", description="Trigger event type")
    message: Optional[str] = None
    risk_level: Optional[str] = None


class NotificationItem(BaseModel):
    id: str
    title: str
    body: str
    category: str
    is_read: bool = False


class NotificationOutput(BaseModel):
    user_id: str
    notifications: list[NotificationItem] = Field(default_factory=list)
