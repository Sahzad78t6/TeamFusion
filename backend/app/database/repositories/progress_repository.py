from app.config.constants import COLLECTION_REFLECTIONS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now


class ProgressRepository:
    async def save_progress(self, user_id: str, data: dict) -> dict:
        doc = {
            "id": generate_uuid(),
            "user_id": user_id,
            "data": data,
            "created_at": get_utc_now(),
        }
        collection = get_collection(COLLECTION_REFLECTIONS)
        if collection is not None:
            await collection.insert_one(doc)
        else:
            mock_store = get_mock_collection(COLLECTION_REFLECTIONS)
            mock_store.append(doc)
        return doc


progress_repository = ProgressRepository()
