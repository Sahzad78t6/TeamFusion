import logging
from app.agents.planner.schemas import PlannerInput
from app.agents.planner.tools import generate_ai_roadmap
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.planner_repository import planner_repository
from app.memory.memory_manager import memory_manager

logger = logging.getLogger(__name__)

class PlannerAgent:
    async def create_and_save_plan(self, user_id: str, goals: list[str] | None = None, raise_on_error: bool = False) -> dict:
        logger.info(f"PlannerAgent creating roadmap for user {user_id}")
        identity = await identity_repository.get_by_user_id(user_id) or {}

        target_role = identity.get("target_role") or identity.get("goal") or "AI Engineer"
        skills = identity.get("skills", ["Python", "FastAPI"])

        # Pydantic validation before calling Groq or Mongo
        user_goals = goals if goals is not None else (identity.get("interests") or [f"Master {target_role}"])
        validated_input = PlannerInput(goals=user_goals, target_role=target_role, skills=skills)

        roadmap = generate_ai_roadmap(
            goals=validated_input.goals,
            target_role=validated_input.target_role,
            skills=validated_input.skills,
            raise_on_error=raise_on_error
        )

        plan_doc = {
            "user_id": user_id,
            "goals": validated_input.goals,
            "tasks": roadmap.get("tasks", []),
            "ai_feedback": roadmap.get("ai_feedback", "Roadmap generated successfully."),
            "degraded": roadmap.get("degraded", False),
            "reason": roadmap.get("reason")
        }

        saved_plan = await planner_repository.save_plan(user_id, plan_doc)

        # Mem0 call wrapped safely
        memory_manager.save_user_fact(
            user_id,
            f"Created daily learning plan with {len(plan_doc['tasks'])} tasks for {target_role}."
        )

        return saved_plan

planner_agent = PlannerAgent()
