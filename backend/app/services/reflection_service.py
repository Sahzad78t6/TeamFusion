import logging
from app.database.repositories.reflection_repository import reflection_repository
from app.agents.reflection.agent import reflection_agent

logger = logging.getLogger(__name__)

class ReflectionService:
    async def create_reflection(self, user_id: str, data: dict) -> dict:
        logger.info(f"Processing daily reflection for user_id: {user_id}")
        return await reflection_agent.process_and_save(user_id, data)

    async def get_user_reflections(self, user_id: str) -> list[dict]:
        return await reflection_repository.get_reflections_by_user(user_id)

reflection_service = ReflectionService()
