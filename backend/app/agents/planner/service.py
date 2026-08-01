"""Service layer for Planner Agent."""
import logging
from app.agents.planner.agent import planner_agent

logger = logging.getLogger(__name__)


class PlannerService:
    async def create_plan(self, user_id: str, data: dict) -> dict:
        """Delegate plan creation to the agent."""
        goals = data.get("goals") or ([data["goal"]] if "goal" in data else None)
        input_data = {"user_id": user_id, "goals": goals}
        result = await planner_agent.execute(input_data)
        return result.data


planner_service = PlannerService()
