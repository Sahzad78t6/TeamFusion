import logging
from app.utils.helpers import generate_uuid, get_utc_now
from app.llm.groq_client import groq_llm
from app.exceptions import LLMJSONParseError, LLMUnavailableError

logger = logging.getLogger(__name__)

def generate_proactive_notifications(
    user_id: str,
    streak: int = 1,
    latest_task: str = "",
    risk_level: str = "low",
    opportunity_title: str = "",
    raise_on_error: bool = False
) -> list[dict]:
    prompt = (
        f"You are GrowthOS Notification Agent. Generate 3 personalized, context-aware notification objects for a user with: "
        f"Learning streak: {streak} days, Next roadmap task: '{latest_task}', Burnout risk level: '{risk_level}', Top job/career match: '{opportunity_title}'. "
        f"Return ONLY a JSON array of objects with keys: "
        f"'title' (string), 'message' (string personalized to their specific state), 'type' (string: 'milestone'/'task_reminder'/'burnout_alert'/'opportunity')."
    )

    result = groq_llm.generate_json(
        prompt=prompt,
        system_instruction="You are GrowthOS Notification Agent. Generate personalized user notifications based on user context.",
        raise_on_error=raise_on_error
    )

    if isinstance(result, list) and len(result) >= 1 and isinstance(result[0], dict):
        notifications = []
        for item in result:
            notifications.append({
                "id": generate_uuid(),
                "user_id": user_id,
                "title": item.get("title", "GrowthOS Update"),
                "message": item.get("message", "Check your daily progress and roadmap."),
                "type": item.get("type", "milestone"),
                "read": False,
                "created_at": get_utc_now(),
                "degraded": False
            })
        return notifications

    if raise_on_error:
        raise LLMJSONParseError("Notification Agent failed to parse valid JSON notifications array from Groq response.")

    reason = groq_llm.last_degraded_reason or "llm_unavailable"
    logger.error(f"Notification LLM generation degraded (reason: {reason}).")
    items = []
    if streak > 0:
        items.append({
            "id": generate_uuid(),
            "user_id": user_id,
            "title": f"{streak}-Day Learning Streak! 🔥",
            "message": f"Great consistency! You've logged active focus sessions {streak} days in a row.",
            "type": "milestone",
            "read": False,
            "created_at": get_utc_now(),
            "degraded": True,
            "reason": reason
        })

    if latest_task:
        items.append({
            "id": generate_uuid(),
            "user_id": user_id,
            "title": "Upcoming Roadmap Focus Item",
            "message": f"Next priority item on your AI roadmap: '{latest_task}'.",
            "type": "task_reminder",
            "read": False,
            "created_at": get_utc_now(),
            "degraded": True,
            "reason": reason
        })

    if risk_level.upper() in ("HIGH_RISK", "HIGH"):
        items.append({
            "id": generate_uuid(),
            "user_id": user_id,
            "title": "Burnout Alert Indicator ⚠️",
            "message": "High study hours or low energy detected. Take a rest break to optimize recovery.",
            "type": "burnout_alert",
            "read": False,
            "created_at": get_utc_now(),
            "degraded": True,
            "reason": reason
        })

    if opportunity_title:
        items.append({
            "id": generate_uuid(),
            "user_id": user_id,
            "title": "New Career Match Discovered 🎯",
            "message": f"Opportunity Agent matched you with: '{opportunity_title}'.",
            "type": "opportunity",
            "read": False,
            "created_at": get_utc_now(),
            "degraded": True,
            "reason": reason
        })

    if not items:
        items.append({
            "id": generate_uuid(),
            "user_id": user_id,
            "title": "Daily GrowthOS Check-in",
            "message": "Complete your daily reflection and view your personalized roadmap.",
            "type": "reflection_prompt",
            "read": False,
            "created_at": get_utc_now(),
            "degraded": True,
            "reason": reason
        })

    return items
