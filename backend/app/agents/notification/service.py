import logging
from app.agents.notification.agent import notification_agent

logger = logging.getLogger(__name__)

class NotificationService:
    async def get_user_notifications(self, user_id: str) -> dict:
        notifications = await notification_agent.get_and_sync_notifications(user_id)
        return {"user_id": user_id, "notifications": notifications}

notification_service = NotificationService()
