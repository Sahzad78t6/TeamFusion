"""Tools for the Notification Agent."""
import uuid
import logging

logger = logging.getLogger(__name__)


def generate_trigger_notifications(context: dict) -> list[dict]:
    """
    Generate deterministic notifications based on event context.
    Currently deterministic, but can be augmented with LLM for varied tones.
    """
    event_type = context.get("event_type", "general")
    notifications = []
    
    if event_type == "reflection_submitted":
        notifications.append({
            "id": str(uuid.uuid4())[:8],
            "title": "Reflection Recorded 📝",
            "body": "Great job! Your reflection helps tailor your roadmap.",
            "category": "progress",
            "is_read": False,
        })
        if context.get("risk_level") == "high":
            notifications.append({
                "id": str(uuid.uuid4())[:8],
                "title": "Burnout Alert ⚠️",
                "body": "Your energy levels seem low. Consider resting today.",
                "category": "alert",
                "is_read": False,
            })
            
    elif event_type == "plan_created":
        notifications.append({
            "id": str(uuid.uuid4())[:8],
            "title": "New Roadmap Ready 🗺️",
            "body": "Your personalized learning roadmap has been generated.",
            "category": "progress",
            "is_read": False,
        })
        
    elif event_type == "onboarding_completed":
        notifications.append({
            "id": str(uuid.uuid4())[:8],
            "title": "Welcome to GrowthOS! 🚀",
            "body": "Your Identity Twin has been created. Let's start growing.",
            "category": "system",
            "is_read": False,
        })
        
    else:
        notifications.append({
            "id": str(uuid.uuid4())[:8],
            "title": "System Update",
            "body": context.get("message", "You have a new update in GrowthOS."),
            "category": "general",
            "is_read": False,
        })
        
    return notifications
