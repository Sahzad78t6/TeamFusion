"""
User State Retriever — GrowthOS Context Engine
Executes user-scoped retrievals across authentic MongoDB collections concurrently.
"""
import asyncio
import logging
from typing import Any

from app.config.constants import COLLECTION_ASSESSMENT_SUBMISSIONS
from app.database.repositories.user_repository import user_repository
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.planner_repository import planner_repository
from app.database.repositories.recommendation_repository import recommendation_repository
from app.database.repositories.reflection_repository import reflection_repository
from app.database.repositories.analytics_repository import analytics_repository
from app.database.repositories.learning_activity_repository import learning_activity_repository
from app.services.institution_service import institution_service

logger = logging.getLogger(__name__)


class UserStateRetriever:
    """
    Retrieves real state strictly scoped to authenticated user_id from MongoDB.
    Never fabricates missing values.
    """

    async def retrieve_raw_user_state(self, user_id: str) -> dict[str, Any]:
        """
        Gathers user documents concurrently:
        1. users
        2. identity_twins
        3. learning_plans
        4. recommendations
        5. reflections
        6. analytics
        7. assessment_submissions
        8. learning_activity (completed resources)
        """
        logger.info(f"[UserStateRetriever] Fetching state for user={user_id}")

        user_task = user_repository.get_by_id(user_id)
        identity_task = identity_repository.get_identity_twin_for_user(user_id)
        plans_task = planner_repository.get_plans_by_user(user_id)
        recs_task = recommendation_repository.get_by_user(user_id)
        reflections_task = reflection_repository.get_reflections_by_user(user_id)
        analytics_task = analytics_repository.get_analytics_for_user(user_id)
        submissions_task = institution_service._list(COLLECTION_ASSESSMENT_SUBMISSIONS, {"student_id": user_id})
        completed_task = learning_activity_repository.get_completed_resource_ids(user_id)

        results = await asyncio.gather(
            user_task,
            identity_task,
            plans_task,
            recs_task,
            reflections_task,
            analytics_task,
            submissions_task,
            completed_task,
            return_exceptions=True
        )

        user_doc = results[0] if isinstance(results[0], dict) else {}
        identity_doc = results[1] if isinstance(results[1], dict) else {}
        plans = results[2] if isinstance(results[2], list) else []
        recs = results[3] if isinstance(results[3], dict) else {}
        reflections = results[4] if isinstance(results[4], list) else []
        analytics = results[5] if isinstance(results[5], dict) else {}
        submissions = results[6] if isinstance(results[6], list) else []
        completed_resources = list(results[7]) if isinstance(results[7], set) else []

        # Strip any MongoDB ObjectIds
        for doc in [user_doc, identity_doc, recs, analytics]:
            if isinstance(doc, dict):
                doc.pop("_id", None)
        for sub in submissions:
            if isinstance(sub, dict):
                sub.pop("_id", None)

        return {
            "user": user_doc,
            "identity_twin": identity_doc,
            "learning_plans": plans,
            "recommendations": recs,
            "reflections": reflections,
            "analytics": analytics,
            "assessment_submissions": submissions,
            "completed_resources": completed_resources
        }


user_state_retriever = UserStateRetriever()
