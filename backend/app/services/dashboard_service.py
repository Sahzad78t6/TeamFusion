import logging
from app.database.repositories.user_repository import user_repository
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.analytics_repository import analytics_repository
from app.services.planner_service import planner_service
from app.services.recommendation_service import recommendation_service
from app.services.notification_service import notification_service
from app.utils.serialization import clean_for_api

logger = logging.getLogger(__name__)


class DashboardService:
    async def get_dashboard_summary(self, user_id: str) -> dict:
        logger.info(f"Assembling real dashboard metrics for user_id: {user_id}")
        user = await user_repository.get_by_id(user_id) or {}
        identity = await identity_repository.get_by_user_id(user_id) or {}
        analytics = await analytics_repository.get_analytics_for_user(user_id)
        plans = await planner_service.get_user_plans(user_id)
        recommendations = await recommendation_service.get_recommendations(user_id)
        notifications = await notification_service.get_user_notifications(user_id)

        return clean_for_api({
            "user_id": user_id,
            "user_name": user.get("name") or "GrowthOS Builder",
            "user_email": user.get("email") or "",
            "goal": identity.get("goal") or identity.get("target_role") or "AI Leader",
            "learning_streak": analytics.get("streak_days", 1),
            "completed_tasks_count": analytics.get("tasks_completed_count", 0),
            "growth_score": analytics.get("growth_score", 85.0),
            "analytics": analytics,
            "identity_twin": identity,
            "roadmap": plans[0] if plans else None,
            "recent_plan": plans[0] if plans else None,
            "recommendations": recommendations.get("recommendations", []),
            "top_recommendations": recommendations.get("recommendations", [])[:3],
            "notifications": notifications.get("notifications", []),
            "unread_notifications_count": notifications.get("unread_count", 0),
        })


dashboard_service = DashboardService()