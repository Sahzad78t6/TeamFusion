"""
Learning Curator Agent — GrowthOS
Curates personalized learning resources for users.
"""
import logging
from app.agents.learning_curator.tools import curate_resources
from app.database.repositories.planner_repository import planner_repository
from app.database.repositories.learning_repository import learning_repository
from app.schemas.models import AgentResponse, LearningBundle
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


class LearningCuratorAgent:
    """Input: Roadmap/Plan. Output: Personalized learning resources."""

    async def execute(self, input_data: dict) -> AgentResponse:
        """Standardized agent entry point."""
        logger.info(f"LearningCuratorAgent.execute() called")
        user_id = input_data.get("user_id", "")
        
        try:
            plans = await planner_repository.get_plans_by_user(user_id)
            plan = plans[-1] if plans else {}
            target_role = plan.get("target_role", "AI Engineer")
            tasks = plan.get("tasks", [])

            resources = await curate_resources(target_role, tasks)
            
            bundle = LearningBundle(
                resources=resources,
                ai_feedback="Curated learning resources based on your roadmap."
            )
            
            bundle_doc = {
                "user_id": user_id,
                "target_role": target_role,
                **bundle.model_dump()
            }
            await learning_repository.save_learning(user_id, bundle_doc)

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
            return AgentResponse(
                success=False,
                agent="learning_curator",
                timestamp=get_utc_now(),
                data={"error": str(e)},
            )

    async def curate_and_save(self, user_id: str) -> dict:
        """Legacy method — delegates to execute()."""
        result = await self.execute({"user_id": user_id})
        return result.data if result.success else {}

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
