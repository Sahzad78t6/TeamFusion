from app.database.repositories.recommendation_repository import recommendation_repository
from app.agents.learning_curator.agent import learning_curator_agent

class RecommendationService:
    async def get_recommendations(self, user_id: str, target_role: str = "AI Engineer") -> dict:
        existing = await recommendation_repository.get_by_user(user_id)
        if existing:
            return existing
        
        recs = learning_curator_agent.curate(user_id, target_role)
        return await recommendation_repository.save_recommendations(user_id, recs)

recommendation_service = RecommendationService()
