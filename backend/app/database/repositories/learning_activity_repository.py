from typing import Any
from app.config.constants import COLLECTION_LEARNING_ACTIVITY
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now

class LearningActivityRepository:
    """
    Repository for tracking granular user learning activity and resource completion.
    Collection: learning_activity
    Fields:
      - id: str
      - user_id: str
      - resource_id: str
      - action: str ('opened', 'progress', 'completed')
      - progress: float (0.0 to 100.0)
      - time_spent_minutes: float
      - started_at: str (ISO)
      - completed_at: str | None (ISO)
    """

    async def log_activity(
        self,
        user_id: str,
        resource_id: str,
        action: str = "completed",
        progress: float = 100.0,
        time_spent_minutes: float = 0.0,
        started_at: str | None = None,
        completed_at: str | None = None
    ) -> dict[str, Any]:
        now = get_utc_now()
        doc = {
            "id": generate_uuid(),
            "user_id": user_id,
            "resource_id": resource_id,
            "action": action,
            "progress": progress,
            "time_spent_minutes": time_spent_minutes,
            "started_at": started_at or now,
            "completed_at": completed_at or (now if action == "completed" or progress >= 100.0 else None),
            "created_at": now
        }

        col = get_collection(COLLECTION_LEARNING_ACTIVITY)
        if col is not None:
            await col.update_one(
                {"user_id": user_id, "resource_id": resource_id},
                {"$set": doc},
                upsert=True
            )
            doc.pop("_id", None)
        else:
            mock = get_mock_collection(COLLECTION_LEARNING_ACTIVITY)
            mock[:] = [m for m in mock if not (m.get("user_id") == user_id and m.get("resource_id") == resource_id)]
            clean_doc = dict(doc)
            clean_doc.pop("_id", None)
            mock.append(clean_doc)

        return doc

    async def get_completed_resource_ids(self, user_id: str) -> set[str]:
        """Returns the set of resource_ids completed by the user."""
        completed: set[str] = set()
        col = get_collection(COLLECTION_LEARNING_ACTIVITY)
        if col is not None:
            cursor = col.find(
                {
                    "user_id": user_id,
                    "$or": [
                        {"action": "completed"},
                        {"progress": {"$gte": 100.0}},
                        {"completed_at": {"$ne": None}}
                    ]
                },
                {"resource_id": 1, "_id": 0}
            )
            docs = await cursor.to_list(length=1000)
            for d in docs:
                if d.get("resource_id"):
                    completed.add(d["resource_id"])
        else:
            mock = get_mock_collection(COLLECTION_LEARNING_ACTIVITY)
            for m in mock:
                if m.get("user_id") == user_id:
                    if m.get("action") == "completed" or (m.get("progress", 0) >= 100) or m.get("completed_at"):
                        if m.get("resource_id"):
                            completed.add(m["resource_id"])

        return completed

    async def get_user_activities(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve recent learning activities for user."""
        col = get_collection(COLLECTION_LEARNING_ACTIVITY)
        if col is not None:
            cursor = col.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1).limit(limit)
            return await cursor.to_list(length=limit)
        else:
            mock = get_mock_collection(COLLECTION_LEARNING_ACTIVITY)
            return [m for m in mock if m.get("user_id") == user_id][:limit]


learning_activity_repository = LearningActivityRepository()
