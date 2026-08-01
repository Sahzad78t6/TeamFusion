from pydantic import BaseModel, Field
from typing import Optional

class PlannerInput(BaseModel):
    goals: list[str] = Field(min_length=1, description="List of target learning goals")
    target_role: Optional[str] = Field(default="AI Architect", max_length=200)
    skills: Optional[list[str]] = Field(default_factory=list)

class TaskItemSchema(BaseModel):
    id: str
    title: str = Field(min_length=1)
    category: str = Field(default="Engineering")
    duration_mins: int = Field(default=30, ge=5, le=480)
    priority: str = Field(default="medium")
    completed: bool = False

class RoadmapOutput(BaseModel):
    ai_feedback: str
    tasks: list[TaskItemSchema]
    degraded: bool = False
    reason: Optional[str] = None
