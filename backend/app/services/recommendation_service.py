import logging
from app.database.repositories.recommendation_repository import recommendation_repository
from app.agents.learning_curator.agent import learning_curator_agent

logger = logging.getLogger(__name__)

class RecommendationService:
    async def get_recommendations(self, user_id: str) -> dict:
        existing = await recommendation_repository.get_by_user(user_id)
        if existing:
            return existing
        
        logger.info(f"Generating new recommendations for user_id: {user_id}")
        return await learning_curator_agent.curate_and_save(user_id)

recommendation_service = RecommendationService()
