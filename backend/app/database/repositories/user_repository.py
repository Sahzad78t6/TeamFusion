from app.config.constants import COLLECTION_USERS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now

class UserRepository:
    async def create_user(self, user_data: dict) -> dict:
        user_doc = {
            "id": user_data.get("id") or generate_uuid(),
            "name": user_data["name"],
            "email": user_data["email"].lower(),
            "hashed_password": user_data["hashed_password"],
            "created_at": get_utc_now()
        }
        collection = get_collection(COLLECTION_USERS)
        if collection is not None:
            await collection.insert_one(user_doc)
        else:
            mock_store = get_mock_collection(COLLECTION_USERS)
            mock_store.append(user_doc)
        return user_doc

    async def get_by_email(self, email: str) -> dict | None:
        collection = get_collection(COLLECTION_USERS)
        if collection is not None:
            return await collection.find_one({"email": email.lower()})
        else:
            mock_store = get_mock_collection(COLLECTION_USERS)
            for user in mock_store:
                if user["email"] == email.lower():
                    return user
            return None

    async def get_by_id(self, user_id: str) -> dict | None:
        collection = get_collection(COLLECTION_USERS)
        if collection is not None:
            return await collection.find_one({"id": user_id})
        else:
            mock_store = get_mock_collection(COLLECTION_USERS)
            for user in mock_store:
                if user["id"] == user_id:
                    return user
            return None

user_repository = UserRepository()
