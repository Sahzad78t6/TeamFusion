"""
Learning Curator Agent — GrowthOS
Curates personalized learning resources for users.
"""
import logging
from app.agents.learning_curator.tools import curate_resources
from app.database.repositories.planner_repository import planner_repository
from app.database.repositories.learning_repository import learning_repository
from app.database.repositories.recommendation_repository import recommendation_repository
from app.services.curator_engine import curator_engine
from app.schemas.models import AgentResponse, LearningBundle
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


class LearningCuratorAgent:
    """Input: Roadmap/Plan. Output: Personalized learning resources."""

    async def execute(self, input_data: dict) -> AgentResponse:
        """Standardized agent entry point."""
        logger.info("LearningCuratorAgent.execute() called")
        user_id = input_data.get("user_id", "")
        
        try:
            topic = input_data.get("topic", "")
            plans = await planner_repository.get_plans_by_user(user_id)
            plan = plans[-1] if plans else {}
            target_role = plan.get("target_role", "Machine Learning Engineer")
            tasks = plan.get("tasks", [])

            resources = await curate_resources(target_role=target_role, tasks=tasks, user_id=user_id, topic=topic)

            bundle_doc = {
                "user_id": user_id,
                "target_role": target_role,
                "resources": resources,
                "recommendations": resources,
                "generated_at": get_utc_now(),
                "ai_feedback": f"Curated {len(resources)} personalized resources for your learning goals."
            }
            await learning_repository.save_learning(user_id, bundle_doc)
            await recommendation_repository.save_recommendations(
                user_id=user_id,
                recommendations=resources,
                target_role=target_role,
                ai_feedback=bundle_doc["ai_feedback"]
            )

            return AgentResponse(
                success=True,
                agent="learning_curator",
                timestamp=get_utc_now(),
                data=bundle_doc,
                database_updates=["recommendations"],
                next_recommended_agent="opportunity",
            )

        except Exception as e:
            logger.error(f"LearningCuratorAgent.execute() failed: {e}", exc_info=True)
            fallback_resources = curator_engine._format_seed_resources(
                skill_gap=input_data.get("topic") or "Python & AI Engineering",
                prefs={}
            )
            fallback_doc = {
                "user_id": user_id,
                "target_role": "Machine Learning Engineer",
                "resources": fallback_resources,
                "recommendations": fallback_resources,
                "generated_at": get_utc_now(),
                "ai_feedback": f"Curated foundational resources (live search provider degraded: {str(e)[:60]})."
            }
            try:
                await recommendation_repository.save_recommendations(
                    user_id=user_id,
                    recommendations=fallback_resources,
                    target_role="Machine Learning Engineer",
                    ai_feedback=fallback_doc["ai_feedback"]
                )
            except Exception as save_err:
                logger.warning(f"Failed to persist fallback recommendations: {save_err}")

            return AgentResponse(
                success=True,
                agent="learning_curator",
                timestamp=get_utc_now(),
                data=fallback_doc,
                database_updates=["recommendations"],
            )

    async def curate_resources(self, user_id: str, topic: str = "") -> dict:
        result = await self.execute({"user_id": user_id, "topic": topic})
        return result.data if result.success else {"resources": []}

    async def curate_and_save(self, user_id: str) -> dict:
        """Legacy method — delegates to execute()."""
        result = await self.execute({"user_id": user_id})
        data = result.data if result.success else {}
        if data and "generated_at" not in data:
            data["generated_at"] = get_utc_now()
        return data

    async def curate_for_user(self, user_id: str) -> LearningBundle | None:
        """Legacy method — delegates to execute()."""
        result = await self.execute({"user_id": user_id})
        if result.success:
            return LearningBundle(resources=result.data.get("resources", []), ai_feedback=result.data.get("ai_feedback", ""))
        return None

    async def get_bundle(self, user_id: str) -> LearningBundle | None:
        data = await learning_repository.get_by_user_id(user_id)
        if data:
            return LearningBundle(resources=data.get("resources", []), ai_feedback=data.get("ai_feedback", ""))
        return None


learning_curator_agent = LearningCuratorAgent()
