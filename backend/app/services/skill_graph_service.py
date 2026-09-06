"""
Skill Graph Service — GrowthOS
Manages learner skill hierarchy, mastery scoring, evidence tracking, and skill progress persistence.
"""
import logging
from typing import Any
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import get_utc_now
from app.schemas.models import SkillNode

logger = logging.getLogger(__name__)

DEFAULT_SKILLS = [
    {"skill_id": "python_base", "name": "Python Fundamentals", "mastery": 0.45, "confidence": 0.6},
    {"skill_id": "python_loops", "name": "Loops & Logic", "mastery": 0.50, "confidence": 0.7},
    {"skill_id": "ds_algo", "name": "Data Structures & Algorithms", "mastery": 0.35, "confidence": 0.4},
    {"skill_id": "recursion", "name": "Recursion", "mastery": 0.20, "confidence": 0.3},
    {"skill_id": "ml_basics", "name": "Machine Learning Foundations", "mastery": 0.40, "confidence": 0.5},
    {"skill_id": "web_api", "name": "REST API & Backend Architecture", "mastery": 0.60, "confidence": 0.75},
]


class SkillGraphService:
    def __init__(self):
        self.collection_name = "skill_progress"

    async def get_user_skills(self, user_id: str) -> list[dict[str, Any]]:
        """Fetch user's skill graph nodes from MongoDB. Seed default nodes if none exist."""
        col = get_collection(self.collection_name)
        if col is not None:
            doc = await col.find_one({"user_id": user_id})
            if doc and "skills" in doc:
                return doc["skills"]
            initial_doc = {"user_id": user_id, "skills": DEFAULT_SKILLS, "updated_at": get_utc_now()}
            await col.insert_one(initial_doc)
            return DEFAULT_SKILLS
        else:
            mock = get_mock_collection(self.collection_name)
            for doc in mock:
                if doc.get("user_id") == user_id:
                    return doc.get("skills", DEFAULT_SKILLS)
            initial_doc = {"user_id": user_id, "skills": DEFAULT_SKILLS, "updated_at": get_utc_now()}
            mock.append(initial_doc)
            return DEFAULT_SKILLS

    async def update_skill_mastery(
        self,
        user_id: str,
        skill_name: str,
        delta_mastery: float,
        evidence: str | None = None
    ) -> dict[str, Any]:
        """Increase or adjust mastery for a specific skill node."""
        skills = await self.get_user_skills(user_id)
        updated = False
        target_skill = None

        for s in skills:
            if s["name"].lower() == skill_name.lower() or s["skill_id"].lower() == skill_name.lower():
                s["mastery"] = round(min(1.0, max(0.0, s["mastery"] + delta_mastery)), 2)
                s["confidence"] = round(min(1.0, max(0.1, s["confidence"] + (delta_mastery * 0.5))), 2)
                s["last_assessed"] = get_utc_now()
                if evidence:
                    s.setdefault("evidence", []).append(evidence)
                target_skill = s
                updated = True
                break

        if not updated:
            new_node = SkillNode(
                skill_id=skill_name.lower().replace(" ", "_"),
                name=skill_name,
                mastery=min(1.0, max(0.1, delta_mastery)),
                confidence=0.5,
                last_assessed=get_utc_now(),
                evidence=[evidence] if evidence else []
            ).model_dump()
            skills.append(new_node)
            target_skill = new_node

        col = get_collection(self.collection_name)
        if col is not None:
            await col.update_one(
                {"user_id": user_id},
                {"$set": {"skills": skills, "updated_at": get_utc_now()}},
                upsert=True
            )
        else:
            mock = get_mock_collection(self.collection_name)
            found = False
            for m in mock:
                if m.get("user_id") == user_id:
                    m["skills"] = skills
                    m["updated_at"] = get_utc_now()
                    found = True
                    break
            if not found:
                mock.append({"user_id": user_id, "skills": skills, "updated_at": get_utc_now()})

        logger.info(f"Updated skill {skill_name} for user {user_id}: mastery -> {target_skill.get('mastery') if target_skill else 0}")
        return target_skill or {}

    async def calculate_skill_alignment(self, user_id: str, target_role: str = "") -> float:
        """Calculates transparent percentage alignment with target role required skills."""
        skills = await self.get_user_skills(user_id)
        if not skills:
            return 0.5

        avg_mastery = sum(s.get("mastery", 0.0) for s in skills) / len(skills)
        return round(avg_mastery, 2)


skill_graph_service = SkillGraphService()

