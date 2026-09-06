"""
Reflection Agent — GrowthOS
Processes daily reflections, provides AI insights, and updates ML burnout metrics.
"""
import logging
from app.agents.reflection.tools import generate_reflection_insights
from app.database.repositories.reflection_repository import reflection_repository
from app.database.repositories.analytics_repository import analytics_repository
from app.ml.inference import ml_inference
from app.memory.memory_manager import memory_manager
from app.schemas.models import AgentResponse
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


class ReflectionAgent:
    """Input: Daily reflection data. Output: AI Insights & updated analytics."""

    async def execute(self, input_data: dict) -> AgentResponse:
        """Standardized agent entry point."""
        logger.info(f"ReflectionAgent.execute() called")
        user_id = input_data.get("user_id", "")
        memory_updates = []
        database_updates = []

        try:
            # Generate AI insight using LLM
            insight = await generate_reflection_insights(input_data)
            
            # Update ML metrics (burnout, growth)
            analytics = await analytics_repository.get_analytics_for_user(user_id)
            tasks_completed = analytics.get("tasks_completed_count", 0) + len(input_data.get("completed_tasks", []))
            total_hours = analytics.get("total_study_hours", 0.0) + input_data.get("study_hours", 0.0)
            streak = analytics.get("streak_days", 0) + 1
            
            ml_results = ml_inference.run_full_analytics_inference(
                tasks_completed=tasks_completed,
                total_hours=total_hours,
                streak_days=streak,
                mood_score=input_data.get("mood_score", 4),
                energy_level=input_data.get("energy_level", 4)
            )
            
            # Save reflection doc
            doc = {
                **input_data,
                "ai_insight": insight,
                "risk_level": ml_results["burnout_risk_level"],
                "burnout_risk_score": ml_results["burnout_risk_score"],
            }
            reflection = await reflection_repository.create_reflection(user_id, doc)
            database_updates.append("reflections")

            # Update analytics DB
            await analytics_repository.update_analytics(
                user_id=user_id,
                add_hours=input_data.get("study_hours", 0.0),
                completed_count=len(input_data.get("completed_tasks", [])),
                risk_level=ml_results["burnout_risk_level"]
            )
            database_updates.append("analytics")

            # If burnout risk is high or notable insights exist, save a memory fact
            if ml_results["burnout_risk_level"] == "high":
                fact = f"User showed high burnout risk on {get_utc_now()[:10]} due to low mood and energy."
                memory_manager.save_user_fact(user_id, fact, {"type": "burnout_risk"})
                memory_updates.append(fact)

            # Log activity event
            from app.services.activity_service import activity_service
            await activity_service.log_event(
                user_id=user_id,
                event_type="reflection_submitted",
                metadata={"mood": input_data.get("mood", "neutral"), "insight": insight}
            )

            # Extract memory snippet for Mem0
            from app.memory.service import memory_service
            notes = input_data.get("reflection_text") or input_data.get("notes") or input_data.get("summary") or ""
            if len(notes) > 10:
                memory_service.add_memory(user_id, f"Learner reflection note: '{notes[:120]}'")

            return AgentResponse(
                success=True,
                agent="reflection",
                timestamp=get_utc_now(),
                data=reflection,
                memory_updates=memory_updates,
                database_updates=database_updates,
                next_recommended_agent="notification",
            )
        except Exception as e:
            logger.error(f"ReflectionAgent.execute() failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                agent="reflection",
                timestamp=get_utc_now(),
                data={"error": str(e)},
            )

    async def process_reflection(self, user_id: str, reflection_text: str, mood: str = "neutral") -> dict:
        input_data = {
            "user_id": user_id,
            "reflection_text": reflection_text,
            "summary": reflection_text,
            "mood": mood,
            "notes": reflection_text
        }
        res = await self.execute(input_data)
        return res.data if res.success else {}

    async def get_user_reflections(self, user_id: str) -> list[dict]:
        return await reflection_repository.get_reflections_by_user(user_id)

    async def process_and_save(self, user_id: str, data: dict) -> dict:
        """Legacy method — delegates to execute()."""
        notes = data.get("notes") or data.get("reflection") or ""
        if notes and "mood_score" not in data:
            mood, energy = extract_sentiment_scores(notes)
            data_with_scores = {"mood_score": mood, "energy_level": energy, **data}
        else:
            data_with_scores = data
            mood = data.get("mood_score", 4)

        input_data = {"user_id": user_id, **data_with_scores}
        result = await self.execute(input_data)
        doc = dict(result.data) if result.success and isinstance(result.data, dict) else {}
        if doc and "mood_score" not in doc:
            doc["mood_score"] = mood
        return doc


reflection_agent = ReflectionAgent()


def extract_sentiment_scores(notes: str) -> tuple[int, int]:
    """Helper to estimate mood and energy scores from notes text."""
    text = (notes or "").lower()
    negative_words = ["stressed", "burnt out", "exhausted", "overwhelmed", "tired", "sad", "bad", "frustrated"]
    positive_words = ["great", "energized", "loving", "happy", "productive", "good", "excited", "awesome"]

    neg_count = sum(1 for word in negative_words if word in text)
    pos_count = sum(1 for word in positive_words if word in text)

    if neg_count > pos_count:
        return (1, 1)
    elif pos_count > neg_count:
        return (5, 5)
    return (3, 3)

