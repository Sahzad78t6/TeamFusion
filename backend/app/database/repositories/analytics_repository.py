from app.config.constants import COLLECTION_ANALYTICS
from app.database.collections import get_collection, get_mock_collection

class AnalyticsRepository:
    async def get_analytics_for_user(self, user_id: str) -> dict:
        collection = get_collection(COLLECTION_ANALYTICS)
        if collection is not None:
            doc = await collection.find_one({"user_id": user_id})
            if doc:
                return doc

        mock_store = get_mock_collection(COLLECTION_ANALYTICS)
        for item in mock_store:
            if item["user_id"] == user_id:
                return item

        # Default placeholder analytics dataset
        default_analytics = {
            "user_id": user_id,
            "growth_score": 88.5,
            "burnout_risk_score": 15.2,
            "burnout_risk_level": "low",
            "weekly_hours_logged": 34.5,
            "tasks_completed_count": 28,
            "streak_days": 12,
            "skill_growth_trends": {
                "Python": 92.0,
                "AI/ML": 85.0,
                "FastAPI": 78.0,
                "React": 80.0
            }
        }
        return default_analytics

analytics_repository = AnalyticsRepository()
