from app.agents.notification.tools import generate_proactive_notifications

class NotificationAgent:
    def get_notifications(self, user_id: str) -> list[dict]:
        return generate_proactive_notifications(user_id)

notification_agent = NotificationAgent()
