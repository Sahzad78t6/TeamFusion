import logging
from app.agents.reflection.tools import compute_burnout_risk_indicator
from app.llm.gemini import gemini_llm
from app.database.repositories.reflection_repository import reflection_repository
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.analytics_repository import analytics_repository
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)

class ReflectionAgent:
    async def process_and_save(self, user_id: str, data: dict) -> dict:
        logger.info(f"ReflectionAgent processing daily reflection for user {user_id}")
        
        notes = data.get("reflection") or data.get("notes", "")
        mood_score = data.get("mood", data.get("mood_score", 4))
        energy_level = data.get("motivation", data.get("energy_level", 4))
        study_hours = float(data.get("study_hours", 2.5))
        completed_tasks = data.get("completed_tasks", [])
        skipped_tasks = data.get("skipped_tasks", [])
        timestamp = data.get("timestamp") or get_utc_now()

        risk = compute_burnout_risk_indicator(mood_score, energy_level, study_hours)
        
        prompt = (
            f"Daily Reflection Notes: '{notes}'. Mood score: {mood_score}/5. Motivation: {energy_level}/5. "
            f"Study hours logged: {study_hours}h. Completed tasks count: {len(completed_tasks)}. Skipped tasks: {len(skipped_tasks)}. "
            f"Calculated burnout risk level: {risk}. "
            f"Provide 2-3 sentences of empathetic, actionable productivity advice."
        )
        
        ai_insight = gemini_llm.generate(
            prompt=prompt,
            system_instruction="You are GrowthOS Reflection Agent. Provide encouraging, supportive productivity and burnout coaching."
        )

        reflection_doc = {
            "user_id": user_id,
            "reflection": notes,
            "notes": notes,
            "mood": mood_score,
            "mood_score": mood_score,
            "motivation": energy_level,
            "energy_level": energy_level,
            "study_hours": study_hours,
            "completed_tasks": completed_tasks,
            "skipped_tasks": skipped_tasks,
            "timestamp": timestamp,
            "risk_level": risk,
            "ai_insight": ai_insight
        }

        saved_reflection = await reflection_repository.create_reflection(user_id, reflection_doc)
        
        # Update user analytics and identity twin drift after each reflection
        await analytics_repository.update_analytics(
            user_id=user_id,
            add_hours=study_hours,
            completed_count=len(completed_tasks),
            risk_level=risk.lower()
        )
        
        await identity_repository.update_identity(user_id, {
            "last_reflection_at": timestamp,
            "burnout_risk_level": risk
        })

        return saved_reflection

reflection_agent = ReflectionAgent()
