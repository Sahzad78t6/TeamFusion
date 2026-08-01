from app.agents.notification.agent import notification_agent

class NotificationService:
    async def get_user_notifications(self, user_id: str) -> dict:
        notifications = notification_agent.get_notifications(user_id)
        unread = len([n for n in notifications if not n.get("read")])
        return {
            "user_id": user_id,
            "notifications": notifications,
            "unread_count": unread
        }

notification_service = NotificationService()
