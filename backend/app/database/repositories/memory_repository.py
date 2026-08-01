from app.config.constants import COLLECTION_MEMORIES
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now


class MemoryRepository:
    async def save_memory(self, user_id: str, fact: str) -> dict:
        doc = {
            "id": generate_uuid(),
            "user_id": user_id,
            "fact": fact,
            "created_at": get_utc_now(),
        }
        collection = get_collection(COLLECTION_MEMORIES)
        if collection is not None:
            await collection.insert_one(doc)
        else:
            mock_store = get_mock_collection(COLLECTION_MEMORIES)
            mock_store.append(doc)
        return doc

    async def get_memories(self, user_id: str) -> list[dict]:
        collection = get_collection(COLLECTION_MEMORIES)
        if collection is not None:
            return [doc async for doc in collection.find({"user_id": user_id})]
        mock_store = get_mock_collection(COLLECTION_MEMORIES)
        return [item for item in mock_store if item.get("user_id") == user_id]


memory_repository = MemoryRepository()
