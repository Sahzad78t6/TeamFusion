from app.config.constants import COLLECTION_IDENTITIES
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now

class IdentityRepository:
    async def create_or_update(self, user_id: str, data: dict) -> dict:
        doc = {
            "id": data.get("id") or generate_uuid(),
            "user_id": user_id,
            "current_role": data.get("current_role", ""),
            "target_role": data.get("target_role", ""),
            "skills": data.get("skills", []),
            "career_goals": data.get("career_goals", []),
            "learning_style": data.get("learning_style", "visual"),
            "updated_at": get_utc_now()
        }
        collection = get_collection(COLLECTION_IDENTITIES)
        if collection is not None:
            await collection.update_one({"user_id": user_id}, {"$set": doc}, upsert=True)
        else:
            mock_store = get_mock_collection(COLLECTION_IDENTITIES)
            mock_store[:] = [item for item in mock_store if item["user_id"] != user_id]
            mock_store.append(doc)
        return doc

    async def get_by_user_id(self, user_id: str) -> dict | None:
        collection = get_collection(COLLECTION_IDENTITIES)
        if collection is not None:
            return await collection.find_one({"user_id": user_id})
        else:
            mock_store = get_mock_collection(COLLECTION_IDENTITIES)
            for item in mock_store:
                if item["user_id"] == user_id:
                    return item
            return None

identity_repository = IdentityRepository()
