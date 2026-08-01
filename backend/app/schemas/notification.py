from pydantic import BaseModel
from typing import List, Optional

class NotificationItem(BaseModel):
    id: str
    title: str
    message: str
    type: str  # info, alert, recommendation, reflection_prompt
    read: bool = False
    created_at: str

class NotificationResponse(BaseModel):
    user_id: str
    notifications: List[NotificationItem]
    unread_count: int
