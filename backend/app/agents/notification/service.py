"""Service layer for Notification Agent."""
import logging
from app.agents.notification.agent import notification_agent

logger = logging.getLogger(__name__)


class NotificationService:
    async def trigger_notification(self, user_id: str, context: dict) -> dict:
        """Delegate notification processing to the agent."""
        input_data = {"user_id": user_id, **context}
        result = await notification_agent.execute(input_data)
        return result.data


notification_service = NotificationService()
