from app.config.constants import COLLECTION_RECOMMENDATIONS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now


class LearningRepository:
    async def save_learning(self, user_id: str, data: dict) -> dict:
        doc = {
            "id": generate_uuid(),
            "user_id": user_id,
            "data": data,
            "created_at": get_utc_now(),
        }
        collection = get_collection(COLLECTION_RECOMMENDATIONS)
        if collection is not None:
            await collection.insert_one(doc)
            doc.pop('_id', None)
        else:
            mock_store = get_mock_collection(COLLECTION_RECOMMENDATIONS)
            clean_doc = dict(doc)
            clean_doc.pop('_id', None)
            mock_store.append(clean_doc)
        return doc

    async def get_by_user_id(self, user_id: str) -> dict | None:
        collection = get_collection(COLLECTION_RECOMMENDATIONS)
        if collection is not None:
            doc = await collection.find_one({"user_id": user_id, "data": {"$exists": True}})
            if doc:
                doc.pop('_id', None)
                return doc.get("data")
            return None
        else:
            mock_store = get_mock_collection(COLLECTION_RECOMMENDATIONS)
            for item in reversed(mock_store):
                if item.get("user_id") == user_id and "data" in item:
                    return item.get("data")
            return None


learning_repository = LearningRepository()
