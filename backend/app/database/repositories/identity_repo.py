import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from app.database.mongodb import get_database
from app.database.collections import COLLECTION_IDENTITY_TWINS

logger = logging.getLogger(__name__)


class IdentityRepository:
    @staticmethod
    async def get_collection():
        db = get_database()
        if db is None:
            raise RuntimeError("Database connection not initialized.")
        return db[COLLECTION_IDENTITY_TWINS]

    @classmethod
    async def get_by_user_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        collection = await cls.get_collection()
        return await collection.find_one({"user_id": user_id})

    @classmethod
    async def create_or_update(cls, user_id: str, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        collection = await cls.get_collection()
        now_iso = datetime.now(timezone.utc).isoformat()
        twin_data["updated_at"] = now_iso
        
        existing = await collection.find_one({"user_id": user_id})
        if existing:
            await collection.update_one({"user_id": user_id}, {"$set": twin_data})
        else:
            twin_data["created_at"] = now_iso
            twin_data["user_id"] = user_id
            await collection.insert_one(twin_data)
        return twin_data
