"""
ML Service — GrowthOS
Central service interfacing with ML models for inactivity/burnout risk prediction and learning progress outcomes.
"""
import logging
from typing import Any
from app.ml.inference import ml_inference
from app.services.activity_service import activity_service
from app.database.repositories.analytics_repository import analytics_repository

logger = logging.getLogger(__name__)


class MLService:
    async def predict_risk(self, user_id: str) -> dict[str, Any]:
        """Predicts inactivity and burnout risk score using real user activity data."""
        days_inactive = await activity_service.get_days_since_last_activity(user_id)
        analytics = await analytics_repository.get_analytics_for_user(user_id)

        tasks_completed = analytics.get("tasks_completed_count", 0)
        total_hours = analytics.get("total_study_hours", 0.0)
        streak_days = analytics.get("streak_days", 0)

        # Base ML inference
        inf_result = ml_inference.run_full_analytics_inference(
            tasks_completed=tasks_completed,
            total_hours=total_hours,
            streak_days=streak_days,
            mood_score=4,
            energy_level=4
        )

        risk_score = inf_result.get("burnout_risk_score", 0.15)
        # Factor in inactivity
        if days_inactive >= 3.0:
            risk_score = min(1.0, risk_score + (days_inactive * 0.1))

        risk_level = "low"
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"

        return {
            "user_id": user_id,
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "days_inactive": round(days_inactive, 1),
            "streak_days": streak_days
        }

    async def predict_learning_outcome(self, user_id: str) -> dict[str, Any]:
        """Predicts learning trajectory based on task completion and consistency."""
        analytics = await analytics_repository.get_analytics_for_user(user_id)
        tasks_completed = analytics.get("tasks_completed_count", 0)
        streak_days = analytics.get("streak_days", 0)

        projected_progress = min(1.0, max(0.1, (tasks_completed * 0.05) + (streak_days * 0.02)))

        return {
            "user_id": user_id,
            "predicted_progress": round(projected_progress, 2),
            "trajectory": "accelerating" if streak_days >= 3 else "steady"
        }


ml_service = MLService()
