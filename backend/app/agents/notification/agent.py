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
        logger.info(f"NotificationAgent.execute() called")
        user_id = input_data.get("user_id", "")
        
        try:
            # Generate notifications based on trigger context
            notifications = generate_trigger_notifications(input_data)
            
            # Save notifications to database
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

    async def trigger(self, user_id: str, context: dict) -> dict:
        """Legacy method — delegates to execute()."""
        input_data = {"user_id": user_id, **context}
        result = await self.execute(input_data)
        return result.data if result.success else {}


notification_agent = NotificationAgent()
