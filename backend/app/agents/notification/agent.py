"""
Notification Agent — GrowthOS
Generates contextual notifications and alerts for users based on triggers.
"""
import logging
from app.agents.notification.tools import generate_trigger_notifications
from app.database.repositories.notification_repository import notification_repository
from app.schemas.models import AgentResponse, NotificationBundle
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


class NotificationAgent:
    """Input: System triggers. Output: Push Notifications & Alerts."""

    async def execute(self, input_data: dict) -> AgentResponse:
        """Standardized agent entry point."""
        logger.info("NotificationAgent.execute() called")
        user_id = input_data.get("user_id", "")
        
        try:
            notifications = generate_trigger_notifications(input_data)
            
            for n in notifications:
                await notification_repository.create_notification(user_id, n["title"], n["body"], n.get("category", "info"))

            bundle = NotificationBundle(
                notifications=notifications,
                ai_feedback="Notifications generated successfully."
            )
            
            return AgentResponse(
                success=True,
                agent="notification",
                timestamp=get_utc_now(),
                data=bundle.model_dump(),
                database_updates=["notifications"],
                next_recommended_agent="conversation",
            )
        except Exception as e:
            logger.error(f"NotificationAgent.execute() failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                agent="notification",
                timestamp=get_utc_now(),
                data={"error": str(e)},
            )

    async def evaluate_and_notify(self, user_id: str, event_type: str, metadata: dict | None = None) -> dict | None:
        """Evaluate event stream and issue intelligent notifications respecting 24-hr cooldowns."""
        metadata = metadata or {}
        db_notifs = await notification_repository.get_by_user(user_id)
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        def has_recent_category(category: str, hours: float = 24.0) -> bool:
            for n in db_notifs:
                if n.get("type") == category or n.get("category") == category:
                    if "created_at" in n:
                        try:
                            ts = datetime.fromisoformat(n["created_at"].replace("Z", "+00:00"))
                            if (now - ts).total_seconds() / 3600.0 < hours:
                                return True
                        except Exception:
                            pass
            return False

        if event_type == "inactivity" or metadata.get("days_inactive", 0) >= 3:
            if not has_recent_category("inactivity", 24.0):
                return await self.create_notification(
                    user_id=user_id,
                    title="Time to Study!",
                    message="You haven't logged a learning session recently. Want to complete a 20-minute task today?",
                    category="inactivity"
                )

        elif event_type == "task_completed":
            if not has_recent_category("achievement", 4.0):
                title = "Task Accomplished! 🎯"
                msg = f"Great work! You completed '{metadata.get('title', 'a learning task')}'."
                return await self.create_notification(user_id=user_id, title=title, message=msg, category="achievement")

        elif event_type == "reflection_submitted":
            mood = metadata.get("mood", "neutral")
            if mood in ["challenged", "low", "frustrated", "tired"]:
                if not has_recent_category("support", 12.0):
                    return await self.create_notification(
                        user_id=user_id,
                        title="Keep Going! 💪",
                        message="Growth takes practice. We've adjusted your study pace based on your reflection.",
                        category="support"
                    )

        return None

    async def create_notification(self, user_id: str, title: str, message: str, category: str = "general") -> dict:
        return await notification_repository.create_notification(user_id, title=title, message=message, notif_type=category)

    async def get_user_notifications(self, user_id: str) -> list[dict]:
        return await notification_repository.get_by_user(user_id)

    async def trigger(self, user_id: str, context: dict) -> dict:
        """Legacy method — delegates to execute()."""
        input_data = {"user_id": user_id, **context}
        result = await self.execute(input_data)
        return result.data if result.success else {}

    async def get_and_sync_notifications(self, user_id: str) -> list[dict]:
        """Fetch notifications for user from repository."""
        return await notification_repository.get_by_user(user_id)


notification_agent = NotificationAgent()
