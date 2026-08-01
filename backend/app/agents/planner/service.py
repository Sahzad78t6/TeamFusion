import logging
from app.agents.planner.agent import planner_agent

logger = logging.getLogger(__name__)

class PlannerService:
    async def create_plan(self, user_id: str, data: dict) -> dict:
        goals = data.get("goals") or ([data["goal"]] if "goal" in data else None)
        return await planner_agent.create_and_save_plan(user_id, goals)

planner_service = PlannerService()
