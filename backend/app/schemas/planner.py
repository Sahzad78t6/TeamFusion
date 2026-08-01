from pydantic import BaseModel
from typing import List, Optional

class TaskItem(BaseModel):
    id: str
    title: str
    completed: bool = False
    duration_mins: int = 30
    priority: str = "medium"

class PlanCreate(BaseModel):
    date: str
    goals: List[str]
    tasks: List[TaskItem] = []

class PlanResponse(BaseModel):
    id: str
    user_id: str
    date: str
    goals: List[str]
    tasks: List[TaskItem]
    ai_feedback: Optional[str] = None
    created_at: str
