"""Pydantic schemas for Opportunity Agent."""
from pydantic import BaseModel, Field


class OpportunityInput(BaseModel):
    user_id: str = Field(default="", description="User identifier")


class MatchedOpportunity(BaseModel):
    id: str
    title: str
    type: str
    match_reason: str


class OpportunityOutput(BaseModel):
    user_id: str
    opportunities: list[MatchedOpportunity] = Field(default_factory=list)
    ai_feedback: str = ""
