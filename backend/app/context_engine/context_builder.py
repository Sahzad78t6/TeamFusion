"""
Context Builder — GrowthOS Context Engine
Assembles raw MongoDB documents into a strongly-typed, normalized UserContext.
"""
import logging
from typing import Any

from app.context_engine.context_models import UserContext
from app.services.curator_context import ROLE_SKILL_BENCHMARKS

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Transforms multi-collection raw states into unified UserContext."""

    def build_context(
        self,
        user_id: str,
        raw_state: dict[str, Any],
        override_topic: str = "",
        override_role: str = ""
    ) -> UserContext:
        user = raw_state.get("user") or {}
        identity = raw_state.get("identity_twin") or {}
        plans = raw_state.get("learning_plans") or []
        latest_plan = plans[-1] if plans else {}
        reflections = raw_state.get("reflections") or []
        analytics = raw_state.get("analytics") or {}
        submissions = raw_state.get("assessment_submissions") or []
        completed_resources = raw_state.get("completed_resources") or []

        # 1. Determine Target Role
        target_role = (
            override_role
            or (override_topic if any(r in override_topic.lower() for r in ["engineer", "developer", "architect", "scientist", "designer"]) else "")
            or identity.get("target_role")
            or identity.get("goal")
            or user.get("target_role")
            or user.get("dreamRole")
            or latest_plan.get("target_role")
            or "Software & AI Engineer"
        ).strip()

        # 2. Determine Career Goal
        career_goal = identity.get("goal") or user.get("dreamRole") or target_role

        # 3. Determine User's Declared Skills
        skills: list[str] = []
        raw_skills = identity.get("skills") or user.get("skills") or []
        if isinstance(raw_skills, list):
            for s in raw_skills:
                if isinstance(s, str) and s.strip():
                    skills.append(s.strip())
                elif isinstance(s, dict) and s.get("skill"):
                    skills.append(s["skill"].strip())

        # 4. Determine Learning Style & Preferences
        learning_style = (
            identity.get("learning_style")
            or user.get("learning_style")
            or "practical"
        ).lower()
        preferred_content = identity.get("preferred_content") or ["Videos", "Interactive Labs", "Articles"]
        learning_preferences = {
            "style": learning_style,
            "preferred_content": preferred_content,
            "available_time": identity.get("available_time") or f"{user.get('available_time_per_week_hours', 10)} hours/week",
            "video_preference": any("video" in p.lower() for p in preferred_content) or "video" in learning_style
        }
        experience_level = identity.get("experience") or user.get("experienceLevel") or "Intermediate"

        # 5. Extract Skill Gaps
        skill_gaps: list[dict[str, Any]] = []
        raw_gaps = identity.get("skill_gaps") or []

        if isinstance(raw_gaps, list) and raw_gaps:
            for g in raw_gaps:
                if isinstance(g, dict) and g.get("skill"):
                    skill_gaps.append({
                        "skill": g["skill"],
                        "gap": g.get("gap", 45),
                        "priority": g.get("priority", "high"),
                        "target_level": g.get("target_level", 85)
                    })
                elif isinstance(g, str) and g.strip():
                    skill_gaps.append({
                        "skill": g.strip(),
                        "gap": 50,
                        "priority": "high",
                        "target_level": 80
                    })

        # Derive role benchmarks if gaps are not yet populated
        if not skill_gaps:
            benchmarks = self._find_role_benchmarks(target_role)
            known_lower = {s.lower() for s in skills}
            for b in benchmarks:
                skill_name = b["skill"]
                is_known = any(k in skill_name.lower() or skill_name.lower() in k for k in known_lower)
                current_level = 70 if is_known else 30
                gap = max(10, b["target_level"] - current_level)
                priority = "high" if gap >= 40 else "medium"
                skill_gaps.append({
                    "skill": skill_name,
                    "gap": gap,
                    "priority": priority,
                    "target_level": b["target_level"]
                })

        skill_gaps.sort(key=lambda x: x.get("gap", 0), reverse=True)

        primary_gap = (
            override_topic
            if (override_topic and not any(r in override_topic.lower() for r in ["engineer", "developer"]))
            else (skill_gaps[0]["skill"] if skill_gaps else f"{target_role} Core Competency")
        )
        secondary_gap = skill_gaps[1]["skill"] if len(skill_gaps) > 1 else primary_gap

        context = UserContext(
            user_id=user_id,
            user=user,
            identity_twin=identity,
            target_role=target_role,
            career_goal=career_goal,
            skills=skills,
            skill_gaps=skill_gaps,
            primary_gap=primary_gap,
            secondary_gap=secondary_gap,
            learning_preferences=learning_preferences,
            learning_style=learning_style,
            preferred_content=preferred_content,
            experience_level=experience_level,
            learning_plan=latest_plan,
            recent_activity=[],
            recent_reflections=reflections[-5:] if reflections else [],
            analytics=analytics,
            assessment_submissions=submissions,
            completed_resources=completed_resources
        )
        context.context_hash = context.compute_hash()
        return context

    def _find_role_benchmarks(self, role: str) -> list[dict[str, Any]]:
        role_lower = role.lower()
        if any(k in role_lower for k in ["frontend", "react", "web developer", "ui"]):
            return ROLE_SKILL_BENCHMARKS["frontend"]
        elif any(k in role_lower for k in ["machine learning", "ml ", "ml engineer", "deep learning"]):
            return ROLE_SKILL_BENCHMARKS["machine learning"]
        elif any(k in role_lower for k in ["ai ", "ai engineer", "agent", "llm"]):
            return ROLE_SKILL_BENCHMARKS["ai"]
        elif any(k in role_lower for k in ["backend", "api", "systems"]):
            return ROLE_SKILL_BENCHMARKS["backend"]
        elif any(k in role_lower for k in ["data science", "data analyst"]):
            return ROLE_SKILL_BENCHMARKS["data science"]
        elif any(k in role_lower for k in ["cyber", "security"]):
            return ROLE_SKILL_BENCHMARKS["cybersecurity"]
        return ROLE_SKILL_BENCHMARKS["general"]


context_builder = ContextBuilder()
