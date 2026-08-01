"""Pydantic schemas for Learning Curator Agent."""
from pydantic import BaseModel, Field


class LearningCuratorInput(BaseModel):
    user_id: str = Field(default="", description="User identifier")


class ResourceItem(BaseModel):
    title: str
    type: str
    reason: str


class LearningCuratorOutput(BaseModel):
    user_id: str
    target_role: str
    resources: list[ResourceItem] = Field(default_factory=list)
    ai_feedback: str = ""
