"""Service layer for Supervisor Agent."""
import logging
from app.agents.supervisor.agent import supervisor_agent

logger = logging.getLogger(__name__)


class SupervisorService:
    async def route_query(self, user_id: str, message: str) -> dict:
        """Delegate routing to the agent."""
        input_data = {"user_id": user_id, "message": message}
        result = await supervisor_agent.execute(input_data)
        return result.data


supervisor_service = SupervisorService()
