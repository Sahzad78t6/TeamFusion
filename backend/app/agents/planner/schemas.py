"""Pydantic schemas for Planner Agent."""
from pydantic import BaseModel, Field
from typing import Optional


class PlannerInput(BaseModel):
    user_id: str = Field(default="", description="User identifier")
    goals: list[str] = Field(min_length=1, description="List of target learning goals")
    target_role: Optional[str] = Field(default="AI Architect", description="Target role")


class TaskItem(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    done: bool = False


class PlannerOutput(BaseModel):
    user_id: str
    target_role: str
    goals: list[str]
    tasks: list[TaskItem] = Field(default_factory=list)
    ai_feedback: str = ""
