from app.services.analytics_service import analytics_service
from app.services.planner_service import planner_service
from app.services.recommendation_service import recommendation_service

class DashboardService:
    async def get_dashboard_summary(self, user_id: str) -> dict:
        analytics = await analytics_service.get_analytics(user_id)
        plans = await planner_service.get_user_plans(user_id)
        recommendations = await recommendation_service.get_recommendations(user_id)
        
        return {
            "user_id": user_id,
            "analytics": analytics,
            "recent_plan": plans[0] if plans else None,
            "top_recommendations": recommendations.get("recommendations", [])[:3]
        }

dashboard_service = DashboardService()
