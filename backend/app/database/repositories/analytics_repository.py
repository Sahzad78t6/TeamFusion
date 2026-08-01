from app.config.constants import COLLECTION_ANALYTICS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import get_utc_now

class AnalyticsRepository:
    async def get_analytics_for_user(self, user_id: str) -> dict:
        collection = get_collection(COLLECTION_ANALYTICS)
        if collection is not None:
            doc = await collection.find_one({"user_id": user_id})
            if doc:
                return doc

        mock_store = get_mock_collection(COLLECTION_ANALYTICS)
        for item in mock_store:
            if item.get("user_id") == user_id:
                return item

        initial_analytics = {
            "user_id": user_id,
            "growth_score": 85.0,
            "burnout_risk_score": 14.0,
            "burnout_risk_level": "low",
            "weekly_hours_logged": 12.5,
            "tasks_completed_count": 8,
            "streak_days": 1,
            "skill_growth_trends": {
                "Python": 85.0,
                "AI/ML": 82.0,
                "FastAPI": 75.0,
                "React": 78.0
            },
            "updated_at": get_utc_now()
        }

        if collection is not None:
            await collection.update_one({"user_id": user_id}, {"$set": initial_analytics}, upsert=True)
        else:
            mock_store.append(initial_analytics)

        return initial_analytics

    async def update_analytics(self, user_id: str, add_hours: float = 0.0, completed_count: int = 0, risk_level: str = "low") -> dict:
        current = await self.get_analytics_for_user(user_id)
        
        new_hours = round(current.get("weekly_hours_logged", 0.0) + add_hours, 1)
        new_tasks = current.get("tasks_completed_count", 0) + completed_count
        new_streak = current.get("streak_days", 1) + (1 if completed_count > 0 else 0)
        
        # Calculate dynamic growth score from streak, hours, and completed tasks
        growth_score = round(min(99.0, max(50.0, 70.0 + (new_streak * 0.5) + (new_tasks * 0.3))), 1)
        
        updated_doc = {
            **current,
            "growth_score": growth_score,
            "burnout_risk_level": risk_level,
            "weekly_hours_logged": new_hours,
            "tasks_completed_count": new_tasks,
            "streak_days": new_streak,
            "updated_at": get_utc_now()
        }
        
        collection = get_collection(COLLECTION_ANALYTICS)
        if collection is not None:
            await collection.update_one({"user_id": user_id}, {"$set": updated_doc}, upsert=True)
        else:
            mock_store = get_mock_collection(COLLECTION_ANALYTICS)
            mock_store[:] = [i for i in mock_store if i.get("user_id") != user_id]
            mock_store.append(updated_doc)

        return updated_doc

analytics_repository = AnalyticsRepository()
