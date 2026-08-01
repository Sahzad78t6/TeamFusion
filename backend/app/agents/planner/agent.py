import logging
from app.agents.planner.tools import generate_ai_roadmap
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.planner_repository import planner_repository

logger = logging.getLogger(__name__)

class PlannerAgent:
    async def create_and_save_plan(self, user_id: str, goals: list[str] | None = None) -> dict:
        logger.info(f"PlannerAgent creating roadmap for user {user_id}")
        identity = await identity_repository.get_by_user_id(user_id) or {}
        
        target_role = identity.get("target_role") or identity.get("goal") or "AI Engineer"
        skills = identity.get("skills", ["Python", "FastAPI"])
        user_goals = goals or identity.get("interests") or [f"Master {target_role}"]

        roadmap = generate_ai_roadmap(goals=user_goals, target_role=target_role, skills=skills)
        
        plan_doc = {
            "user_id": user_id,
            "goals": user_goals,
            "tasks": roadmap.get("tasks", []),
            "ai_feedback": roadmap.get("ai_feedback", "Roadmap generated successfully.")
        }
        
        saved_plan = await planner_repository.save_plan(user_id, plan_doc)
        return saved_plan

planner_agent = PlannerAgent()
