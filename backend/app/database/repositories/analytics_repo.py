import logging
from typing import List, Dict, Any
from app.database.mongodb import get_database
from app.database.collections import COLLECTION_ANALYTICS

logger = logging.getLogger(__name__)


class AnalyticsRepository:
    @staticmethod
    async def get_collection():
        db = get_database()
        if db is None:
            raise RuntimeError("Database connection not initialized.")
        return db[COLLECTION_ANALYTICS]

    @classmethod
    async def log_event(cls, event_doc: Dict[str, Any]) -> Dict[str, Any]:
        collection = await cls.get_collection()
        await collection.insert_one(event_doc)
        return event_doc

    @classmethod
    async def get_user_events(cls, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        collection = await cls.get_collection()
        cursor = collection.find({"user_id": user_id}).limit(limit)
        return await cursor.to_list(length=limit)
