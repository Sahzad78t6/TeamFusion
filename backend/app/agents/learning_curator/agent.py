"""
Learning Curator Agent — GrowthOS
Curates real personalized learning resources tailored to the authenticated user's
Identity Twin, skill gaps, target role, and learning history.
"""
import logging
from app.context_engine import context_engine_service, UserContext
from app.services.curator_engine import curator_engine
from app.database.repositories.planner_repository import planner_repository
from app.database.repositories.learning_repository import learning_repository
from app.database.repositories.recommendation_repository import recommendation_repository
from app.database.repositories.agent_run_repository import agent_run_repository
from app.schemas.models import AgentResponse, LearningBundle
from app.utils.helpers import get_utc_now, generate_uuid

logger = logging.getLogger(__name__)


class LearningCuratorAgent:
    """Input: User context / topic. Output: Real personalized learning resources."""

    async def execute(self, input_data: dict) -> AgentResponse:
        """Standardized agent entry point."""
        user_id = input_data.get("user_id", "")
        topic = input_data.get("topic", "")

        # 1. Synthesize student context strictly from authentic MongoDB collections
        context: UserContext = await context_engine_service.get_user_context(user_id=user_id, topic=topic)

        # 2. Record agent run telemetry
        run_record = await agent_run_repository.start_run(
            user_id=user_id,
            agent_name="learning_curator",
            skills_considered=[context.primary_gap, context.secondary_gap],
            metadata={
                "target_role": context.target_role,
                "learning_style": context.learning_style,
                "context_hash": context.context_hash
            }
        )
        curation_run_id = run_record["id"]

        try:
            logger.info(
                f"[CURATOR_START] user_id={user_id[:8]}... run_id={curation_run_id} "
                f"target_role='{context.target_role}' primary_gap='{context.primary_gap}' "
                f"style='{context.learning_style}' hash={context.context_hash}"
            )

            # 3. Curate candidate resources from YouTube + Web via CuratorEngine
            resources = await curator_engine.curate_personalized_resources(
                user_id=user_id,
                topic=context.primary_gap,
                target_role=context.target_role,
                context=context
            )

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

            # 4. Persist to MongoDB Atlas collections
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

            # 5. Complete agent run telemetry
            await agent_run_repository.complete_run(
                run_id=curation_run_id,
                status="completed",
                resources_generated=len(resources),
                metadata_updates={"curation_run_id": curation_run_id}
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
                database_updates=["recommendations", "agent_runs"],
                next_recommended_agent="opportunity",
            )

        except Exception as e:
            logger.error(f"[CURATOR_ERROR] user_id={user_id}: {e}", exc_info=True)
            fallback_resources = curator_engine._format_domain_seed_resources(context)

            fallback_doc = {
                "user_id": user_id,
                "curation_run_id": curation_run_id,
                "target_role": context.target_role,
                "primary_gap": context.primary_gap,
                "learning_style": context.learning_style,
                "context_hash": context.context_hash,
                "resources": fallback_resources,
                "recommendations": fallback_resources,
                "generated_at": get_utc_now(),
                "ai_feedback": (
                    f"Curated foundational resources for your '{context.target_role}' goal "
                    f"targeting your '{context.primary_gap}' gap."
                )
            }

            try:
                await recommendation_repository.save_recommendations(
                    user_id=user_id,
                    recommendations=fallback_resources,
                    target_role=context.target_role,
                    primary_gap=context.primary_gap,
                    context_hash=context.context_hash,
                    curation_run_id=curation_run_id,
                    ai_feedback=fallback_doc["ai_feedback"]
                )
                await agent_run_repository.complete_run(
                    run_id=curation_run_id,
                    status="fallback",
                    resources_generated=len(fallback_resources),
                    metadata_updates={"error": str(e)}
                )
            except Exception as save_err:
                logger.warning(f"Failed to persist fallback recommendations: {save_err}")

            return AgentResponse(
                success=True,
                agent="learning_curator",
                timestamp=get_utc_now(),
                data=fallback_doc,
                database_updates=["recommendations", "agent_runs"],
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
