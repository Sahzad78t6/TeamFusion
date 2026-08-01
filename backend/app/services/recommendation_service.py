import logging
from typing import List, Dict, Any
from app.database.repositories.recommendation_repo import RecommendationRepository

logger = logging.getLogger(__name__)


class RecommendationService:
    @staticmethod
    async def get_user_recommendations(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return await RecommendationRepository.get_by_user_id(user_id, limit)

    @staticmethod
    async def create_recommendation(data: Dict[str, Any]) -> Dict[str, Any]:
        return await RecommendationRepository.create_recommendation(data)
