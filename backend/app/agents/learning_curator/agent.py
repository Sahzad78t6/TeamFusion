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
        input_context_summary = {
            "target_role": context.target_role,
            "primary_gap": context.primary_gap,
            "secondary_gap": context.secondary_gap,
            "learning_style": context.learning_style,
            "skills": context.skills,
            "context_hash": context.context_hash
        }
        # 2. Record agent run telemetry
        run_record = await agent_run_repository.start_run(
            user_id=user_id,
            agent_name="learning_curator",
            input_context_summary=input_context_summary,
            skills_considered=[context.primary_gap, context.secondary_gap],
            execution_mode="REAL",
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
                context=context,
                agent_run_id=curation_run_id
            )

            queries = getattr(context, "last_queries", [f"{context.primary_gap} tutorial"])
            retrieved_count = getattr(context, "results_retrieved", len(resources))

            bundle_doc = {
                "user_id": user_id,
                "curation_run_id": curation_run_id,
                "agent_run_id": curation_run_id,
                "target_role": context.target_role,
                "primary_gap": context.primary_gap,
                "learning_style": context.learning_style,
                "context_hash": context.context_hash,
                "resources": resources,
                "recommendations": resources,
                "generated_at": get_utc_now(),
                "ai_feedback": (
                    f"Curated {len(resources)} real personalized resources for your {context.target_role} path "
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

            # 5. Complete agent run telemetry (mode: REAL)
            await agent_run_repository.complete_run(
                run_id=curation_run_id,
                status="completed",
                execution_mode="REAL",
                tools_called=["youtube_search", "llm_rerank"],
                queries=queries,
                provider="youtube",
                results_retrieved=retrieved_count,
                results_selected=len(resources),
                decision_summary=f"Selected {len(resources)} resources out of {retrieved_count} candidate results for role '{context.target_role}'",
                database_writes=["recommendations", "agent_runs"],
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
            # Log failure in AgentRun
            queries = getattr(context, "last_queries", [])
            await agent_run_repository.fail_run(
                run_id=curation_run_id,
                error=str(e),
                execution_mode="FAILED",
                tools_called=["youtube_search"],
                queries=queries,
                provider="youtube",
                metadata_updates={"error_class": e.__class__.__name__}
            )
            # ZERO SILENT FALLBACK: Re-raise exception so failures are visible to user and API!
            raise


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
