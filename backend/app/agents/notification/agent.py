import logging
from app.agents.notification.tools import generate_proactive_notifications
from app.database.repositories.analytics_repository import analytics_repository
from app.database.repositories.planner_repository import planner_repository
from app.database.repositories.opportunity_repository import opportunity_repository
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.notification_repository import notification_repository

logger = logging.getLogger(__name__)

class NotificationAgent:
    async def get_and_sync_notifications(self, user_id: str) -> list[dict]:
        logger.info(f"NotificationAgent evaluating dynamic notifications for user {user_id}")
        analytics = await analytics_repository.get_analytics_for_user(user_id)
        plans = await planner_repository.get_plans_by_user(user_id)
        opps_doc = await opportunity_repository.get_by_user(user_id)
        identity = await identity_repository.get_by_user_id(user_id) or {}

        streak = analytics.get("streak_days", 1)
        risk = identity.get("burnout_risk_level") or analytics.get("burnout_risk_level", "low")
        
        latest_task = ""
        if plans and plans[0].get("tasks"):
            uncompleted = [t for t in plans[0]["tasks"] if not t.get("completed")]
            if uncompleted:
                latest_task = uncompleted[0].get("title", "")

        opp_title = ""
        if opps_doc and opps_doc.get("opportunities"):
            opp_title = opps_doc["opportunities"][0].get("title", "")

        generated = generate_proactive_notifications(
            user_id=user_id,
            streak=streak,
            latest_task=latest_task,
            risk_level=risk,
            opportunity_title=opp_title
        )

        saved = await notification_repository.save_notifications(user_id, generated)
        return saved

notification_agent = NotificationAgent()
