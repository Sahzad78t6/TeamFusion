"""Service layer for Reflection Agent."""
import logging
from app.agents.reflection.agent import reflection_agent

logger = logging.getLogger(__name__)


class ReflectionService:
    async def create_reflection(self, user_id: str, data: dict) -> dict:
        """Delegate reflection processing to the agent."""
        input_data = {"user_id": user_id, **data}
        result = await reflection_agent.execute(input_data)
        return result.data


reflection_service = ReflectionService()
