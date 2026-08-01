import logging
from app.agents.reflection.agent import reflection_agent

logger = logging.getLogger(__name__)

class ReflectionService:
    async def create_reflection(self, user_id: str, data: dict) -> dict:
        return await reflection_agent.process_and_save(user_id, data)

reflection_service = ReflectionService()
