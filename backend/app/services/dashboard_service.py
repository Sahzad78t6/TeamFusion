import logging
from typing import Dict, Any
from app.database.repositories.identity_repo import IdentityRepository
from app.database.repositories.recommendation_repo import RecommendationRepository
from app.database.repositories.reflection_repo import ReflectionRepository

logger = logging.getLogger(__name__)


class DashboardService:
    @staticmethod
    async def get_dashboard_overview(user_id: str) -> Dict[str, Any]:
        identity = await IdentityRepository.get_by_user_id(user_id)
        recommendations = await RecommendationRepository.get_by_user_id(user_id, limit=5)
        reflections = await ReflectionRepository.get_by_user_id(user_id, limit=5)
        
        return {
            "user_id": user_id,
            "identity_twin": identity,
            "recent_recommendations": recommendations,
            "recent_reflections": reflections
        }
