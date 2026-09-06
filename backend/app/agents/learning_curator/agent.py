"""
Learning Curator Agent — GrowthOS
Curates real personalized learning resources tailored to the authenticated user's
Identity Twin, skill gaps, target role, and learning history.
"""
import logging
from app.services.curator_context import curator_context_builder, UserLearningContext
from app.services.curator_engine import curator_engine
from app.database.repositories.planner_repository import planner_repository
from app.database.repositories.learning_repository import learning_repository
from app.database.repositories.recommendation_repository import recommendation_repository
from app.schemas.models import AgentResponse, LearningBundle
from app.utils.helpers import get_utc_now, generate_uuid

logger = logging.getLogger(__name__)


class LearningCuratorAgent:
    """Input: User context / topic. Output: Real personalized learning resources."""

    async def execute(self, input_data: dict) -> AgentResponse:
        """Standardized agent entry point."""
        user_id = input_data.get("user_id", "")
        topic = input_data.get("topic", "")

        try:
            # 1. Build authentic student context from Identity Twin, Profile, and Activity
            context: UserLearningContext = await curator_context_builder.build(user_id=user_id, topic=topic)

            logger.info(
                f"[CURATOR_START] user_id={user_id[:8]}... target_role='{context.target_role}' "
                f"primary_gap='{context.primary_gap}' style='{context.learning_style}' "
                f"hash={context.context_hash}"
            )

            # 2. Curate candidate resources from YouTube + Web via CuratorEngine
            resources = await curator_engine.curate_personalized_resources(
                user_id=user_id,
                topic=context.primary_gap,
                target_role=context.target_role
            )

            curation_run_id = f"run_{generate_uuid()[:8]}"
            bundle_doc = {
                "user_id": user_id,
                "curation_run_id": curation_run_id,
                "target_role": context.target_role,
                "primary_gap": context.primary_gap,
                "learning_style": context.learning_style,
                "context_hash": context.context_hash,
                "resources": resources,
                "recommendations": resources,
                "generated_at": get_utc_now(),
                "ai_feedback": (
                    f"Curated {len(resources)} personalized resources for your {context.target_role} path "
                    f"focusing on your '{context.primary_gap}' skill gap."
                )
            }

            # 3. Persist to MongoDB Atlas collections
            await learning_repository.save_learning(user_id, bundle_doc)
            await recommendation_repository.save_recommendations(
                user_id=user_id,
                recommendations=resources,
                target_role=context.target_role,
                primary_gap=context.primary_gap,
                context_hash=context.context_hash,
                curation_run_id=curation_run_id,
                ai_feedback=bundle_doc["ai_feedback"]
            )

            logger.info(
                f"[CURATOR_COMPLETED] user_id={user_id[:8]}... run_id={curation_run_id} "
                f"curated_count={len(resources)} hash={context.context_hash}"
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
            logger.error(f"[CURATOR_ERROR] user_id={user_id}: {e}", exc_info=True)
            fallback_context = await curator_context_builder.build(user_id=user_id, topic=topic)
            fallback_resources = curator_engine._format_domain_seed_resources(fallback_context)
            curation_run_id = f"run_{generate_uuid()[:8]}"

            fallback_doc = {
                "user_id": user_id,
                "curation_run_id": curation_run_id,
                "target_role": fallback_context.target_role,
                "primary_gap": fallback_context.primary_gap,
                "learning_style": fallback_context.learning_style,
                "context_hash": fallback_context.context_hash,
                "resources": fallback_resources,
                "recommendations": fallback_resources,
                "generated_at": get_utc_now(),
                "ai_feedback": (
                    f"Curated foundational resources for your '{fallback_context.target_role}' goal "
                    f"targeting your '{fallback_context.primary_gap}' gap."
                )
            }

            try:
                await recommendation_repository.save_recommendations(
                    user_id=user_id,
                    recommendations=fallback_resources,
                    target_role=fallback_context.target_role,
                    primary_gap=fallback_context.primary_gap,
                    context_hash=fallback_context.context_hash,
                    curation_run_id=curation_run_id,
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
