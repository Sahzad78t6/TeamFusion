"""
Planner Agent — GrowthOS
Generates structured learning roadmaps from user goals and profiles.
"""
import logging
from app.agents.planner.tools import generate_ai_roadmap
from app.database.repositories.user_repository import user_repository
from app.database.repositories.memory_repository import memory_repository
from app.database.repositories.planner_repository import planner_repository
from app.utils.text_normalize import normalize_role_string
from app.schemas.models import AgentResponse, Roadmap
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Input: User Profile + Memory. Output: Roadmap & Daily Tasks."""

    async def execute(self, input_data: dict) -> AgentResponse:
        """Standardized agent entry point."""
        logger.info(f"PlannerAgent.execute() called")
        user_id = input_data.get("user_id", "")
        goals = input_data.get("goals")
        
        try:
            profile = await user_repository.get_by_id(user_id) or {}
            memory = await memory_repository.get_memories(user_id) or {}

            raw_role = profile.get("target_role") or memory.get("long_term", {}).get("target_role") or "AI Engineer"
            target_role = normalize_role_string(raw_role)
            skills = profile.get("skills") or ["Python"]
            user_goals = goals or profile.get("interests") or [f"Master {target_role}"]

            roadmap_data = await generate_ai_roadmap(goals=user_goals, target_role=target_role, skills=skills)

            roadmap = Roadmap(
                tasks=roadmap_data.get("tasks", []),
                ai_feedback=roadmap_data.get("ai_feedback", "Roadmap generated successfully."),
            )

            # Save plan to database
            plan_doc = {
                "user_id": user_id,
                "target_role": target_role,
                "goals": user_goals,
                # Visibility: allows frontend/devtools to verify AI vs fallback
                "ai_generated": roadmap_data.get("ai_generated", False),
                "generation_source": roadmap_data.get("generation_source", "unknown"),
                **roadmap.model_dump()
            }
            await planner_repository.save_plan(user_id, plan_doc)

            return AgentResponse(
                success=True,
                agent="planner",
                timestamp=get_utc_now(),
                data=plan_doc,
                database_updates=["learning_plans"],
                next_recommended_agent="learning_curator",
            )
        except Exception as e:
            logger.error(f"PlannerAgent.execute() failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                agent="planner",
                timestamp=get_utc_now(),
                data={"error": str(e)},
            )

    async def generate_and_store_plan(self, user_id: str, goals: list[str] | None = None) -> dict:
        result = await self.execute({"user_id": user_id, "goals": goals})
        if result.success and result.data:
            from app.services.activity_service import activity_service
            await activity_service.log_event(user_id, "plan_created", {"task_count": len(result.data.get("tasks", []))})
        return result.data if result.success else {}

    async def get_today_plan(self, user_id: str) -> dict:
        plans = await planner_repository.get_plans_by_user(user_id)
        if plans:
            return plans[-1]
        return await self.generate_and_store_plan(user_id)

    async def get_plan(self, user_id: str) -> Roadmap | None:
        data = await planner_repository.get_by_user_id(user_id) if hasattr(planner_repository, 'get_by_user_id') else await self.get_today_plan(user_id)
        if data:
            return Roadmap(tasks=data.get("tasks", []), ai_feedback=data.get("ai_feedback", ""))
        return None

    async def update_task_status(self, user_id: str, task_id: str, completed: bool = True) -> dict:
        from app.services.planner_service import planner_service
        return await planner_service.toggle_task_completion(user_id, task_id, completed)


planner_agent = PlannerAgent()

