"""Pydantic schemas for Supervisor Agent."""
from pydantic import BaseModel, Field


class SupervisorInput(BaseModel):
    user_id: str = Field(default="", description="User identifier")
    message: str = Field(default="", description="User query to route")


class SupervisorOutput(BaseModel):
    routed_to: str = Field(default="conversation", description="Next agent to invoke")
