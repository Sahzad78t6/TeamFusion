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

            # If burnout risk is high, save a memory fact
            if ml_results["burnout_risk_level"] == "high":
                fact = f"User showed high burnout risk on {get_utc_now()[:10]} due to low mood and energy."
                memory_manager.save_user_fact(user_id, fact, {"type": "burnout_risk"})
                memory_updates.append(fact)

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

    async def process_and_save(self, user_id: str, data: dict) -> dict:
        """Legacy method — delegates to execute()."""
        input_data = {"user_id": user_id, **data}
        result = await self.execute(input_data)
        return result.data if result.success else {}


reflection_agent = ReflectionAgent()
