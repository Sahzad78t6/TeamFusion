"""
Core Pydantic models for GrowthOS.
Defines all shared data structures used across agents, services, and API.
"""
from typing import Any
from pydantic import BaseModel, Field
from app.utils.helpers import get_utc_now


# ─── Standardized Agent Response ───────────────────────────────────────────

class AgentResponse(BaseModel):
    """Standardized output format for all GrowthOS agents."""
    success: bool = True
    agent: str = ""
    timestamp: str = Field(default_factory=get_utc_now)
    data: dict[str, Any] = Field(default_factory=dict)
    memory_updates: list[str] = Field(default_factory=list)
    database_updates: list[str] = Field(default_factory=list)
    next_recommended_agent: str = ""


# ─── User & Onboarding ────────────────────────────────────────────────────

class UserProfile(BaseModel):
    target_role: str = Field(default="")
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    learning_style: str = Field(default="hands-on")
    available_time_per_week_hours: int = Field(default=5)
    aspirations: str = Field(default="")


class OnboardingInput(BaseModel):
    user_id: str = Field(default="")
    target_role: str = Field(default="")
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    learning_style: str = Field(default="hands-on")
    available_time_per_week_hours: int = Field(default=5)
    aspirations: str = Field(default="")
    chat_messages: list[dict[str, Any]] = Field(default_factory=list)


# ─── Memory ────────────────────────────────────────────────────────────────

class MemoryEntry(BaseModel):
    user_id: str
    content: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


# ─── Planner ──────────────────────────────────────────────────────────────

class Roadmap(BaseModel):
    tasks: list[dict[str, Any]] = Field(default_factory=list)
    ai_feedback: str = Field(default="")


# ─── Learning Curator ─────────────────────────────────────────────────────

class LearningBundle(BaseModel):
    resources: list[dict[str, Any]] = Field(default_factory=list)
    ai_feedback: str = Field(default="")


# ─── Opportunity ──────────────────────────────────────────────────────────

class OpportunityBundle(BaseModel):
    opportunities: list[dict[str, Any]] = Field(default_factory=list)
    ai_feedback: str = Field(default="")


# ─── Reflection ───────────────────────────────────────────────────────────

class ReflectionInput(BaseModel):
    user_id: str = Field(default="")
    summary: str = Field(default="")
    mood: str = Field(default="")
    completed_task_ids: list[str] = Field(default_factory=list)
    reflection_text: str | None = None


class ProgressReport(BaseModel):
    summary: str = Field(default="")
    next_steps: list[str] = Field(default_factory=list)
    ai_feedback: str = Field(default="")


# ─── Notification ─────────────────────────────────────────────────────────

class Notification(BaseModel):
    title: str = Field(default="")
    body: str = Field(default="")
    message: str = Field(default="")
    category: str = Field(default="general")


class NotificationBundle(BaseModel):
    notifications: list[Notification] = Field(default_factory=list)
    ai_feedback: str = Field(default="")


# ─── Pipeline ─────────────────────────────────────────────────────────────

class PipelineResult(BaseModel):
    user_id: str
    profile: Any = None
    memory: Any = None
    roadmap: Any = None
    learning: Any = None
    opportunities: Any = None
    progress: Any = None
    notifications: Any = None


# ─── Supervisor Contract & Phase 2 Models ──────────────────────────────────

class SupervisorResponse(BaseModel):
    intent: str = Field(default="conversation", description="Identified user intent")
    agent: str = Field(default="conversation", description="Target agent assigned to handle query")
    action: str = Field(default="reply", description="Action taken or proposed")
    result: str = Field(default="", description="Human-readable result summary")
    data: dict[str, Any] = Field(default_factory=dict, description="Structured payload")
    confidence: float = Field(default=1.0, description="Confidence score 0.0 to 1.0")
    requires_confirmation: bool = Field(default=False, description="True if action is high risk and needs confirmation")


class SkillNode(BaseModel):
    skill_id: str
    name: str
    mastery: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    last_assessed: str = Field(default_factory=get_utc_now)
    evidence: list[str] = Field(default_factory=list)


class LearningEventModel(BaseModel):
    user_id: str
    event_type: str
    timestamp: str = Field(default_factory=get_utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRunLog(BaseModel):
    request_id: str
    user_id: str
    supervisor: str = Field(default="supervisor")
    selected_agent: str
    tool_calls: list[str] = Field(default_factory=list)
    duration_ms: float = 0.0
    success: bool = True
    error: str | None = None
    timestamp: str = Field(default_factory=get_utc_now)

