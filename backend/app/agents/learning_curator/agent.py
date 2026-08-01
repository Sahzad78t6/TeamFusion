import logging
from app.agents.learning_curator.tools import generate_ai_recommendations
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.recommendation_repository import recommendation_repository

logger = logging.getLogger(__name__)

class LearningCuratorAgent:
    async def curate_and_save(self, user_id: str) -> dict:
        logger.info(f"LearningCuratorAgent curating resources for user {user_id}")
        identity = await identity_repository.get_by_user_id(user_id) or {}
        
        target_role = identity.get("target_role") or identity.get("goal") or "AI Specialist"
        skills = identity.get("skills", ["Python", "FastAPI"])
        learning_style = identity.get("learning_style", "Hands-on projects")

        recs = generate_ai_recommendations(target_role=target_role, skills=skills, learning_style=learning_style)
        
        saved_doc = await recommendation_repository.save_recommendations(user_id, recs)
        return saved_doc

learning_curator_agent = LearningCuratorAgent()
