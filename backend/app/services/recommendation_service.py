import logging
from datetime import datetime, timezone, timedelta
from app.database.repositories.recommendation_repository import recommendation_repository
from app.agents.learning_curator.agent import learning_curator_agent
from app.services.curator_context import curator_context_builder, UserLearningContext
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)

RECOMMENDATION_TTL_HOURS = 24


class RecommendationService:
    async def get_recommendations(self, user_id: str) -> dict:
        """
        Retrieves recommendations for the authenticated user:
        1. Evaluates current UserLearningContext (target role, skill gaps, learning style).
        2. Inspects existing stored recommendation bundle for this specific user.
        3. Validates context freshness via context_hash matching.
        4. If fresh and within TTL -> returns cached bundle without consuming search quota.
        5. If stale, mismatched context, or missing -> runs fresh curator execution.
        """
        current_context: UserLearningContext = await curator_context_builder.build(user_id)
        existing = await recommendation_repository.get_by_user(user_id)

        if existing and existing.get("recommendations"):
            clean_existing = dict(existing)
            clean_existing.pop("_id", None)

            # Verify context fingerprint match
            stored_hash = clean_existing.get("context_hash")
            is_hash_match = bool(stored_hash and stored_hash == current_context.context_hash)

            # Verify TTL freshness
            is_within_ttl = True
            gen_time_str = clean_existing.get("generated_at")
            if gen_time_str:
                try:
                    gen_time = datetime.fromisoformat(gen_time_str.replace("Z", "+00:00"))
                    if datetime.now(timezone.utc) - gen_time > timedelta(hours=RECOMMENDATION_TTL_HOURS):
                        is_within_ttl = False
                except Exception:
                    is_within_ttl = True

            if is_hash_match and is_within_ttl:
                logger.info(
                    f"[GET_RECOMMENDATIONS] Returning fresh cached bundle for {user_id} "
                    f"(hash={stored_hash}, target_role='{clean_existing.get('target_role')}')"
                )
                if "resources" not in clean_existing:
                    clean_existing["resources"] = clean_existing["recommendations"]
                if "primary_gap" not in clean_existing:
                    clean_existing["primary_gap"] = current_context.primary_gap
                clean_existing["user_id"] = user_id
                return clean_existing
            else:
                logger.info(
                    f"[GET_RECOMMENDATIONS] Stale recommendation detected for {user_id}: "
                    f"stored_hash={stored_hash} vs current_hash={current_context.context_hash}, "
                    f"is_within_ttl={is_within_ttl}. Regenerating."
                )

        logger.info(f"[GET_RECOMMENDATIONS] Generating new personalized recommendations for user_id: {user_id}")
        return await self.refresh_recommendations(user_id)

    async def refresh_recommendations(self, user_id: str, topic: str = "") -> dict:
        """
        Forces full live execution of the LearningCuratorAgent with user context.
        """
        logger.info(f"[REFRESH_RECOMMENDATIONS] Executing curator for user_id: {user_id}, topic: '{topic}'")
        res = await learning_curator_agent.execute({"user_id": user_id, "topic": topic})
        data = res.data if res and res.data else {}

        recs = data.get("recommendations") or data.get("resources") or []
        clean_data = dict(data)
        clean_data.pop("_id", None)
        clean_data["user_id"] = user_id
        clean_data["recommendations"] = recs
        clean_data["resources"] = recs
        if "generated_at" not in clean_data or not clean_data["generated_at"]:
            clean_data["generated_at"] = get_utc_now()

        return clean_data


recommendation_service = RecommendationService()
