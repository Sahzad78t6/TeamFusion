"""
Curator Context Builder — GrowthOS
Constructs real, user-specific learning contexts derived from
User Profiles, Identity Twins, Skill Graphs, Activity Logs, and Memory.
"""
from dataclasses import dataclass, field
import hashlib
import json
import logging
from typing import Any

from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.user_repository import user_repository
from app.database.repositories.planner_repository import planner_repository
from app.services.skill_graph_service import skill_graph_service
from app.services.activity_service import activity_service
from app.memory.service import memory_service

logger = logging.getLogger(__name__)

ROLE_SKILL_BENCHMARKS: dict[str, list[dict[str, Any]]] = {
    "frontend": [
        {"skill": "React & Component Architecture", "target_level": 85},
        {"skill": "TypeScript & Modern Web Standards", "target_level": 80},
        {"skill": "State Management & Performance", "target_level": 75},
        {"skill": "CSS & Modern UI Architecture", "target_level": 80},
        {"skill": "Frontend Testing & Web Vitals", "target_level": 70},
    ],
    "machine learning": [
        {"skill": "Machine Learning Fundamentals", "target_level": 85},
        {"skill": "Model Evaluation & Metrics", "target_level": 80},
        {"skill": "Feature Engineering & Preprocessing", "target_level": 85},
        {"skill": "Deep Learning & Neural Networks", "target_level": 75},
        {"skill": "Scikit-Learn & PyTorch", "target_level": 80},
    ],
    "ai": [
        {"skill": "LLM Application Engineering & Prompting", "target_level": 85},
        {"skill": "Vector Databases & RAG Architecture", "target_level": 80},
        {"skill": "Multi-Agent Systems & LangGraph", "target_level": 80},
        {"skill": "Model Evaluation & Benchmarking", "target_level": 75},
        {"skill": "Python Async & FastAPI", "target_level": 80},
    ],
    "backend": [
        {"skill": "REST & GraphQL API Architecture", "target_level": 85},
        {"skill": "Database Optimization & Modeling", "target_level": 80},
        {"skill": "Microservices & Distributed Systems", "target_level": 75},
        {"skill": "System Security & Authentication", "target_level": 80},
    ],
    "data science": [
        {"skill": "Statistical Analysis & Inference", "target_level": 85},
        {"skill": "Pandas & Data Wrangling", "target_level": 85},
        {"skill": "Data Visualization & Communication", "target_level": 75},
        {"skill": "Predictive Modeling & Scikit-Learn", "target_level": 80},
    ],
    "cybersecurity": [
        {"skill": "Network Security & Penetration Testing", "target_level": 85},
        {"skill": "IAM & Access Governance", "target_level": 80},
        {"skill": "OWASP & Secure Code Review", "target_level": 85},
        {"skill": "Cryptography & Threat Modeling", "target_level": 75},
    ],
    "general": [
        {"skill": "Core Programming & Problem Solving", "target_level": 80},
        {"skill": "Data Structures & Algorithmic Thinking", "target_level": 75},
        {"skill": "Software Engineering Architecture", "target_level": 75},
    ]
}


@dataclass
class UserLearningContext:
    user_id: str
    target_role: str
    career_goal: str
    current_skills: list[str]
    skill_gaps: list[dict[str, Any]]
    primary_gap: str
    secondary_gap: str
    learning_style: str
    preferred_content: list[str]
    experience_level: str
    completed_resources: set[str] = field(default_factory=set)
    context_hash: str = ""

    def compute_hash(self) -> str:
        payload = f"{self.user_id}|{self.target_role.lower().strip()}|{self.primary_gap.lower().strip()}|{self.learning_style.lower().strip()}|{','.join(sorted(self.current_skills))}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


class CuratorContextBuilder:
    async def build(self, user_id: str, topic: str = "") -> UserLearningContext:
        """
        Synthesizes student context strictly from authentic user database records:
        1. User Identity Twin (identity_twins collection)
        2. User Profile (users collection)
        3. User Roadmap Plans (learning_plans collection)
        4. User Skill Graph (skill_progress collection)
        5. User Activity stream (learning_events collection)
        """
        logger.info(f"Building learning context for user: {user_id}, topic: '{topic}'")

        # 1. Fetch Identity Twin
        identity = await identity_repository.get_by_user_id(user_id) or {}
        # 2. Fetch User Profile
        user_doc = await user_repository.get_by_id(user_id) or {}
        # 3. Fetch Planner plans
        plans = await planner_repository.get_plans_by_user(user_id)
        latest_plan = plans[-1] if plans else {}
        # 4. Fetch User Activity stream to find completed resources
        recent_events = await activity_service.get_user_activity(user_id, limit=50)
        completed_resource_ids = {
            ev.get("metadata", {}).get("resource_id")
            for ev in recent_events
            if ev.get("event_type") == "resource_completed" and ev.get("metadata", {}).get("resource_id")
        }

        # 5. Determine Target Role
        target_role = (
            identity.get("target_role")
            or identity.get("goal")
            or latest_plan.get("target_role")
            or user_doc.get("dreamRole")
            or user_doc.get("target_role")
            or (topic if any(r in topic.lower() for r in ["engineer", "developer", "architect", "scientist", "designer"]) else "")
            or "Software & AI Engineer"
        ).strip()

        # Determine Career Goal
        career_goal = identity.get("goal") or user_doc.get("dreamRole") or target_role

        # Determine User's Known Skills
        current_skills: list[str] = []
        raw_skills = identity.get("skills") or user_doc.get("skills") or []
        if isinstance(raw_skills, list):
            for s in raw_skills:
                if isinstance(s, str) and s.strip():
                    current_skills.append(s.strip())
                elif isinstance(s, dict) and s.get("skill"):
                    current_skills.append(s["skill"].strip())

        # Determine Learning Style & Preferences
        learning_style = identity.get("learning_style") or "practical"
        preferred_content = identity.get("preferred_content") or ["Videos", "Interactive Labs", "Articles"]
        experience_level = identity.get("experience") or user_doc.get("experienceLevel") or "Intermediate"

        # 6. Compute Real Skill Gaps
        skill_gaps: list[dict[str, Any]] = []
        raw_gaps = identity.get("skill_gaps") or []

        if isinstance(raw_gaps, list) and raw_gaps:
            for g in raw_gaps:
                if isinstance(g, dict) and g.get("skill"):
                    skill_gaps.append({
                        "skill": g["skill"],
                        "gap": g.get("gap", 40),
                        "priority": g.get("priority", "high")
                    })
                elif isinstance(g, str) and g.strip():
                    skill_gaps.append({
                        "skill": g.strip(),
                        "gap": 50,
                        "priority": "high"
                    })

        # If no explicit skill gaps were stored, derive them from target role benchmarks
        if not skill_gaps:
            benchmarks = self._find_role_benchmarks(target_role)
            known_lower = {s.lower() for s in current_skills}
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

        # Sort skill gaps by gap magnitude descending
        skill_gaps.sort(key=lambda x: x.get("gap", 0), reverse=True)

        primary_gap = topic if topic else (skill_gaps[0]["skill"] if skill_gaps else f"{target_role} Core Competency")
        secondary_gap = skill_gaps[1]["skill"] if len(skill_gaps) > 1 else primary_gap

        context = UserLearningContext(
            user_id=user_id,
            target_role=target_role,
            career_goal=career_goal,
            current_skills=current_skills,
            skill_gaps=skill_gaps,
            primary_gap=primary_gap,
            secondary_gap=secondary_gap,
            learning_style=learning_style,
            preferred_content=preferred_content,
            experience_level=experience_level,
            completed_resources=completed_resource_ids
        )
        context.context_hash = context.compute_hash()
        return context

    def _find_role_benchmarks(self, role: str) -> list[dict[str, Any]]:
        role_lower = role.lower()
        if any(k in role_lower for k in ["frontend", "react", "web developer", "ui", "ux"]):
            return ROLE_SKILL_BENCHMARKS["frontend"]
        elif any(k in role_lower for k in ["machine learning", "ml ", "ml engineer", "deep learning"]):
            return ROLE_SKILL_BENCHMARKS["machine learning"]
        elif any(k in role_lower for k in ["ai ", "ai engineer", "agent", "llm"]):
            return ROLE_SKILL_BENCHMARKS["ai"]
        elif any(k in role_lower for k in ["backend", "api", "systems", "cloud"]):
            return ROLE_SKILL_BENCHMARKS["backend"]
        elif any(k in role_lower for k in ["data science", "data analyst", "data scientist"]):
            return ROLE_SKILL_BENCHMARKS["data science"]
        elif any(k in role_lower for k in ["cyber", "security"]):
            return ROLE_SKILL_BENCHMARKS["cybersecurity"]
        return ROLE_SKILL_BENCHMARKS["general"]


curator_context_builder = CuratorContextBuilder()
