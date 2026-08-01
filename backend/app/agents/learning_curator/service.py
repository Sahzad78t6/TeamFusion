import logging
from app.agents.learning_curator.agent import learning_curator_agent

logger = logging.getLogger(__name__)

class LearningCuratorService:
    async def get_recommendations(self, user_id: str) -> dict:
        return await learning_curator_agent.curate_and_save(user_id)

    async def refresh_recommendations(self, user_id: str) -> dict:
        return await learning_curator_agent.curate_and_save(user_id)

learning_curator_service = LearningCuratorService()
