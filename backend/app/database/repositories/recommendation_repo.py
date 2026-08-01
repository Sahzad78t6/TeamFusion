import logging
from typing import List, Dict, Any
from app.database.mongodb import get_database
from app.database.collections import COLLECTION_RECOMMENDATIONS

logger = logging.getLogger(__name__)


class RecommendationRepository:
    @staticmethod
    async def get_collection():
        db = get_database()
        if db is None:
            raise RuntimeError("Database connection not initialized.")
        return db[COLLECTION_RECOMMENDATIONS]

    @classmethod
    async def get_by_user_id(cls, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        collection = await cls.get_collection()
        cursor = collection.find({"user_id": user_id}).limit(limit)
        return await cursor.to_list(length=limit)

    @classmethod
    async def create_recommendation(cls, rec_doc: Dict[str, Any]) -> Dict[str, Any]:
        collection = await cls.get_collection()
        await collection.insert_one(rec_doc)
        return rec_doc
