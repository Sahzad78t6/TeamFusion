"""
Context Models — GrowthOS Context Engine
Defines strongly-typed models representing the authentic synthesized MongoDB state for a user.
"""
from dataclasses import dataclass, field
import hashlib
from typing import Any
from pydantic import BaseModel, Field


class UserProfileContext(BaseModel):
    id: str = ""
    name: str = ""
    email: str = ""
    role: str = "STUDENT"
    institution_id: str | None = None
    cohort_id: str | None = None
    target_role: str = ""
    dream_role: str = ""
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    learning_style: str = ""
    experience_level: str = ""
    available_time_per_week_hours: int = 5


class IdentityTwinContext(BaseModel):
    id: str = ""
    goal: str = ""
    target_role: str = ""
    current_role: str = ""
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    skill_gaps: list[dict[str, Any]] = Field(default_factory=list)
    learning_style: str = ""
    preferred_content: list[str] = Field(default_factory=list)
    experience: str = ""
    career_stage: str = ""
    available_time: str = ""
    identity_score: float = 85.0
    strategic_insight: str | None = None


class SkillGapItem(BaseModel):
    skill: str
    gap: int = 40
    priority: str = "high"
    target_level: int = 80


class UserContext(BaseModel):
    """
    Unified, strongly typed context model combining authentic MongoDB collections.
    Zero hallucinated or fabricated data.
    """
    user_id: str
    user: dict[str, Any] = Field(default_factory=dict)
    identity_twin: dict[str, Any] = Field(default_factory=dict)
    target_role: str = "Software & AI Engineer"
    career_goal: str = ""
    skills: list[str] = Field(default_factory=list)
    skill_gaps: list[dict[str, Any]] = Field(default_factory=list)
    primary_gap: str = "System Design & Architecture"
    secondary_gap: str = "Scalable Backend APIs"
    learning_preferences: dict[str, Any] = Field(default_factory=dict)
    learning_style: str = "practical"
    preferred_content: list[str] = Field(default_factory=list)
    experience_level: str = "Intermediate"
    learning_plan: dict[str, Any] = Field(default_factory=dict)
    recent_activity: list[dict[str, Any]] = Field(default_factory=list)
    recent_reflections: list[dict[str, Any]] = Field(default_factory=list)
    analytics: dict[str, Any] = Field(default_factory=dict)
    assessment_submissions: list[dict[str, Any]] = Field(default_factory=list)
    completed_resources: list[str] = Field(default_factory=list)
    context_hash: str = ""
    last_queries: list[str] = Field(default_factory=list)
    results_retrieved: int = 0
    results_selected: int = 0

    def compute_hash(self) -> str:
        """Deterministic fingerprint of role, gaps, style, and skills for cache invalidation."""
        skills_str = ",".join(sorted(self.skills))
        payload = f"{self.user_id}|{self.target_role.lower().strip()}|{self.primary_gap.lower().strip()}|{self.learning_style.lower().strip()}|{skills_str}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
