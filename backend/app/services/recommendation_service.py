import logging
from app.database.repositories.recommendation_repository import recommendation_repository
from app.agents.learning_curator.agent import learning_curator_agent
from app.services.curator_engine import curator_engine
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


class RecommendationService:
    async def get_recommendations(self, user_id: str) -> dict:
        existing = await recommendation_repository.get_by_user(user_id)
        if existing and existing.get("recommendations"):
            clean_existing = dict(existing)
            clean_existing.pop("_id", None)
            if "resources" not in clean_existing:
                clean_existing["resources"] = clean_existing["recommendations"]
            if "generated_at" not in clean_existing:
                clean_existing["generated_at"] = get_utc_now()
            return clean_existing
        
        logger.info(f"Generating new recommendations for user_id: {user_id}")
        return await self.refresh_recommendations(user_id)

    async def refresh_recommendations(self, user_id: str, topic: str = "") -> dict:
        logger.info(f"Forcing LearningCuratorAgent refresh for user_id: {user_id}, topic: '{topic}'")
        res = await learning_curator_agent.execute({"user_id": user_id, "topic": topic})
        data = res.data if res and res.data else {}

        # Validate recommendations list
        recs = data.get("recommendations") or data.get("resources") or []
        if not recs:
            logger.info("No recommendations returned by curator. Applying verified educational fallback.")
            recs = curator_engine._format_seed_resources(skill_gap=topic or "Python & AI Engineering", prefs={})
            data["recommendations"] = recs
            data["resources"] = recs

        clean_data = dict(data)
        clean_data.pop("_id", None)
        clean_data["user_id"] = user_id
        clean_data["recommendations"] = recs
        clean_data["resources"] = recs
        if "generated_at" not in clean_data or not clean_data["generated_at"]:
            clean_data["generated_at"] = get_utc_now()

        return clean_data


recommendation_service = RecommendationService()
