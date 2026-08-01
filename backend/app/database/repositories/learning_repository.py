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
        else:
            mock_store = get_mock_collection(COLLECTION_RECOMMENDATIONS)
            mock_store.append(doc)
        return doc


learning_repository = LearningRepository()
