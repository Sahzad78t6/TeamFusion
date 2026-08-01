from app.config.constants import COLLECTION_PLANS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now

class PlannerRepository:
    async def save_plan(self, user_id: str, data: dict) -> dict:
        doc = {
            "id": data.get("id") or generate_uuid(),
            "user_id": user_id,
            "date": data.get("date", get_utc_now()[:10]),
            "goals": data.get("goals", []),
            "tasks": data.get("tasks", []),
            "ai_feedback": data.get("ai_feedback", "Plan optimized by AI Supervisor."),
            "created_at": get_utc_now()
        }
        collection = get_collection(COLLECTION_PLANS)
        if collection is not None:
            await collection.insert_one(doc)
        else:
            mock_store = get_mock_collection(COLLECTION_PLANS)
            mock_store.append(doc)
        return doc

    async def get_plans_by_user(self, user_id: str) -> list[dict]:
        collection = get_collection(COLLECTION_PLANS)
        if collection is not None:
            cursor = collection.find({"user_id": user_id})
            return await cursor.to_list(length=100)
        else:
            mock_store = get_mock_collection(COLLECTION_PLANS)
            return [item for item in mock_store if item["user_id"] == user_id]

planner_repository = PlannerRepository()
