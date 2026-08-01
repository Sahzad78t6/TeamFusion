from app.utils.helpers import generate_uuid, get_utc_now

def generate_proactive_notifications(user_id: str, streak: int = 1, latest_task: str = "", risk_level: str = "low", opportunity_title: str = "") -> list[dict]:
    items = []
    
    # 1. Learning Streak Notification
    if streak > 0:
        items.append({
            "id": generate_uuid(),
            "user_id": user_id,
            "title": f"{streak}-Day Learning Streak! 🔥",
            "message": f"Great consistency! You've logged active focus sessions {streak} days in a row.",
            "type": "milestone",
            "read": False,
            "created_at": get_utc_now()
        })

    # 2. Upcoming Roadmap Task Notification
    if latest_task:
        items.append({
            "id": generate_uuid(),
            "user_id": user_id,
            "title": "Upcoming Roadmap Focus Item",
            "message": f"Next priority item on your AI roadmap: '{latest_task}'.",
            "type": "task_reminder",
            "read": False,
            "created_at": get_utc_now()
        })

    # 3. Burnout Alert Notification
    if risk_level.upper() in ("HIGH_RISK", "HIGH"):
        items.append({
            "id": generate_uuid(),
            "user_id": user_id,
            "title": "Burnout Alert Indicator ⚠️",
            "message": "High study hours or low energy detected. Take a 15-minute rest break to optimize recovery.",
            "type": "burnout_alert",
            "read": False,
            "created_at": get_utc_now()
        })

    # 4. New Matching Opportunity Notification
    if opportunity_title:
        items.append({
            "id": generate_uuid(),
            "user_id": user_id,
            "title": "New Career Match Discovered 🎯",
            "message": f"Opportunity Agent matched you with: '{opportunity_title}'.",
            "type": "opportunity",
            "read": False,
            "created_at": get_utc_now()
        })

    if not items:
        items.append({
            "id": generate_uuid(),
            "user_id": user_id,
            "title": "Daily GrowthOS Check-in",
            "message": "Complete your daily reflection and view your personalized roadmap.",
            "type": "reflection_prompt",
            "read": False,
            "created_at": get_utc_now()
        })

    return items
