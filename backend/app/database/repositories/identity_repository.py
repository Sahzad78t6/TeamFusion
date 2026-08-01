from app.config.constants import COLLECTION_IDENTITIES
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now

class IdentityRepository:
    async def create_or_update(self, user_id: str, data: dict) -> dict:
        doc = {
            "id": data.get("id") or generate_uuid(),
            "user_id": user_id,
            "goal": data.get("goal") or data.get("target_role") or "AI Specialist & Tech Leader",
            "interests": data.get("interests", ["AI", "Machine Learning", "System Design"]),
            "skills": data.get("skills", ["Python", "FastAPI"]),
            "experience": data.get("experience", "Intermediate"),
            "learning_style": data.get("learning_style", "Hands-on projects"),
            "career_stage": data.get("career_stage", "Mid-Level Engineer"),
            "available_time": data.get("available_time", "10-15 hours/week"),
            "preferred_content": data.get("preferred_content", ["Courses", "Interactive Labs"]),
            "language": data.get("language", "English"),
            "current_role": data.get("current_role") or "Software Engineer",
            "target_role": data.get("target_role") or data.get("goal") or "Senior AI Architect",
            "identity_score": data.get("identity_score", 85.0),
            "identity_drift_percentage": data.get("identity_drift_percentage", 12.0),
            "updated_at": get_utc_now()
        }
        collection = get_collection(COLLECTION_IDENTITIES)
        if collection is not None:
            await collection.update_one({"user_id": user_id}, {"$set": doc}, upsert=True)
        else:
            mock_store = get_mock_collection(COLLECTION_IDENTITIES)
            mock_store[:] = [item for item in mock_store if item.get("user_id") != user_id]
            mock_store.append(doc)
        return doc

    async def get_by_user_id(self, user_id: str) -> dict | None:
        collection = get_collection(COLLECTION_IDENTITIES)
        if collection is not None:
            return await collection.find_one({"user_id": user_id})
        else:
            mock_store = get_mock_collection(COLLECTION_IDENTITIES)
            for item in mock_store:
                if item.get("user_id") == user_id:
                    return item
            return None

    async def update_identity(self, user_id: str, updates: dict) -> dict | None:
        updates["updated_at"] = get_utc_now()
        collection = get_collection(COLLECTION_IDENTITIES)
        if collection is not None:
            await collection.update_one({"user_id": user_id}, {"$set": updates}, upsert=True)
            return await collection.find_one({"user_id": user_id})
        else:
            mock_store = get_mock_collection(COLLECTION_IDENTITIES)
            for item in mock_store:
                if item.get("user_id") == user_id:
                    item.update(updates)
                    return item
            return None

identity_repository = IdentityRepository()
