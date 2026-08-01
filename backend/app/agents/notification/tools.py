from app.utils.helpers import generate_uuid, get_utc_now

def generate_proactive_notifications(user_id: str) -> list[dict]:
    return [
        {
            "id": generate_uuid(),
            "title": "12-Day Streak Achieved! 🔥",
            "message": "Outstanding consistency! You've logged focus sessions 12 days in a row.",
            "type": "info",
            "read": False,
            "created_at": get_utc_now()
        },
        {
            "id": generate_uuid(),
            "title": "Time for Daily Reflection",
            "message": "Spend 2 minutes recording your energy level and key wins today.",
            "type": "reflection_prompt",
            "read": False,
            "created_at": get_utc_now()
        }
    ]
