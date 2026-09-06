import logging
from app.agents.notification.agent import notification_agent

logger = logging.getLogger(__name__)

class NotificationService:
    async def get_user_notifications(self, user_id: str) -> dict:
        logger.info(f"Fetching notifications for user_id: {user_id}")
        notifications = await notification_agent.get_and_sync_notifications(user_id)
        unread = len([n for n in notifications if not n.get("read")])
        return {
            "user_id": user_id,
            "notifications": notifications,
            "unread_count": unread
        }

    async def mark_as_read(self, user_id: str, notification_id: str) -> dict:
        from app.database.repositories.notification_repository import notification_repository
        success = await notification_repository.mark_as_read(user_id, notification_id)
        return {"success": success, "notification_id": notification_id}

    async def mark_all_as_read(self, user_id: str) -> dict:
        from app.database.repositories.notification_repository import notification_repository
        success = await notification_repository.mark_all_as_read(user_id)
        return {"success": success}


notification_service = NotificationService()

