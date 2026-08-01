from app.database.repositories.analytics_repository import analytics_repository
from app.ml.inference import ml_inference

class AnalyticsService:
    async def get_analytics(self, user_id: str) -> dict:
        data = await analytics_repository.get_analytics_for_user(user_id)
        ml_results = ml_inference.run_full_analytics_inference(
            tasks_completed=data.get("tasks_completed_count", 28),
            total_hours=data.get("weekly_hours_logged", 34.5),
            streak_days=data.get("streak_days", 12),
            mood_score=4,
            energy_level=4
        )
        data.update(ml_results)
        return data

analytics_service = AnalyticsService()
