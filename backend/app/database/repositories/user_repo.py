import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from app.database.mongodb import get_database
from app.database.collections import COLLECTION_USERS

logger = logging.getLogger(__name__)


class UserRepository:
    @staticmethod
    async def get_collection():
        db = get_database()
        if db is None:
            raise RuntimeError("Database connection not initialized.")
        return db[COLLECTION_USERS]

    @classmethod
    async def find_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        collection = await cls.get_collection()
        return await collection.find_one({"email": email.lower().strip()})

    @classmethod
    async def find_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        collection = await cls.get_collection()
        return await collection.find_one({"id": user_id})

    @classmethod
    async def create_user(cls, user_doc: Dict[str, Any]) -> Dict[str, Any]:
        collection = await cls.get_collection()
        await collection.insert_one(user_doc)
        return user_doc

    @classmethod
    async def update_refresh_token(cls, user_id: str, refresh_token: Optional[str]) -> bool:
        collection = await cls.get_collection()
        now_iso = datetime.now(timezone.utc).isoformat()
        result = await collection.update_one(
            {"id": user_id},
            {"$set": {"refresh_token": refresh_token, "updated_at": now_iso}}
        )
        return result.modified_count > 0
