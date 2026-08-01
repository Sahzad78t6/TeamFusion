import logging
from app.database.repositories.planner_repository import planner_repository
from app.agents.planner.agent import planner_agent

logger = logging.getLogger(__name__)

class PlannerService:
    async def create_plan(self, user_id: str, plan_data: dict) -> dict:
        logger.info(f"Generating learning plan for user {user_id}")
        goals = plan_data.get("goals", [])
        return await planner_agent.create_and_save_plan(user_id, goals)

    async def get_user_plans(self, user_id: str) -> list[dict]:
        plans = await planner_repository.get_plans_by_user(user_id)
        if not plans:
            # Generate initial plan if none exists for the user yet
            initial_plan = await planner_agent.create_and_save_plan(user_id)
            return [initial_plan]
        return plans

planner_service = PlannerService()
