from fastapi import APIRouter, Depends, status

from app.auth import get_current_user
from app.db import get_db
from app.routers.recommendation import get_user_recommendations

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("", status_code=status.HTTP_200_OK)
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = str(current_user["_id"])
    progress = await db["user_progress"].find_one({"user_id": user_id})

    goal = (progress.get("goal") if progress else None) or current_user.get("goal") or "ml_engineer"
    year = (progress.get("year") if progress else None) or current_user.get("year") or "1st Year"

    curriculum = await db["curriculum"].find_one({"goal": goal, "year": year})
    if not curriculum:
        curriculum = await db["curriculum"].find_one({"goal": "ml_engineer", "year": "1st Year"})

    sequence = curriculum.get("sequence", []) if curriculum else []
    current_topic_index = progress.get("current_topic_index", 0) if progress else 0
    completed_topics = progress.get("completed_topics", []) if progress else []

    total_topics = len(sequence)
    progress_percent = round((len(completed_topics) / total_topics) * 100) if total_topics > 0 else 0

    if sequence and current_topic_index < total_topics:
        current_topic_item = sequence[current_topic_index]
        current_topic_label = current_topic_item["label"]
        current_topic_code = current_topic_item["topic_code"]
        is_completed = False
    else:
        current_topic_label = "Completed"
        current_topic_code = "completed"
        is_completed = True

    # Pull recommendations for dashboard preview
    rec_data = await get_user_recommendations(current_user, db)
    resources = rec_data.get("resources", [])

    return {
        "current_topic": current_topic_label,
        "progress_percent": progress_percent,
        "streak": current_user.get("streak", 0) or 0,
        "goal": goal,
        "year": year,
        # Integrated fields for AppContext.tsx and Dashboard.tsx
        "identity_twin": {
            "target_role": current_user.get("target_role") or goal,
            "goal": goal,
            "identity_score": 85,
            "identity_drift_percentage": 12,
        },
        "analytics": {
            "growth_score": 88,
            "weekly_hours_logged": 14,
            "burnout_risk_score": 15,
            "streak_days": current_user.get("streak", 0) or 0,
        },
        "roadmap": {
            "tasks": [
                {
                    "id": current_topic_code,
                    "title": current_topic_label,
                    "completed": False,
                    "duration_mins": 45,
                    "priority": "high",
                    "category": "Curriculum",
                }
            ] if not is_completed else []
        },
        "recommendations": resources[:4],
    }
