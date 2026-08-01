from app.config.constants import COLLECTION_REFLECTIONS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now

class ReflectionRepository:
    async def create_reflection(self, user_id: str, data: dict) -> dict:
        doc = {
            "id": generate_uuid(),
            "user_id": user_id,
            "mood_score": data.get("mood_score", 4),
            "energy_level": data.get("energy_level", 4),
            "mood": data.get("mood", data.get("mood_score", 4)),
            "motivation": data.get("motivation", data.get("energy_level", 4)),
            "reflection": data.get("reflection", data.get("notes", "")),
            "notes": data.get("notes", ""),
            "wins": data.get("wins", ""),
            "challenges": data.get("challenges", ""),
            "study_hours": data.get("study_hours", 0.0),
            "completed_tasks": data.get("completed_tasks", []),
            "skipped_tasks": data.get("skipped_tasks", []),
            "timestamp": data.get("timestamp", get_utc_now()),
            "risk_level": data.get("risk_level", "LOW"),
            "ai_insight": data.get("ai_insight", "Great momentum! Keep standard work-rest cycles."),
            "created_at": get_utc_now()
        }
        collection = get_collection(COLLECTION_REFLECTIONS)
        if collection is not None:
            await collection.insert_one(doc)
        else:
            mock_store = get_mock_collection(COLLECTION_REFLECTIONS)
            mock_store.append(doc)
        return doc

    async def get_reflections_by_user(self, user_id: str) -> list[dict]:
        collection = get_collection(COLLECTION_REFLECTIONS)
        if collection is not None:
            cursor = collection.find({"user_id": user_id})
            return await cursor.to_list(length=100)
        else:
            mock_store = get_mock_collection(COLLECTION_REFLECTIONS)
            return [item for item in mock_store if item["user_id"] == user_id]

reflection_repository = ReflectionRepository()
