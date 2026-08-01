"""Service layer for Learning Curator Agent."""
import logging
from app.agents.learning_curator.agent import learning_curator_agent

logger = logging.getLogger(__name__)


class LearningCuratorService:
    async def curate_resources(self, user_id: str) -> dict:
        """Delegate learning curation to the agent."""
        input_data = {"user_id": user_id}
        result = await learning_curator_agent.execute(input_data)
        return result.data


learning_curator_service = LearningCuratorService()
