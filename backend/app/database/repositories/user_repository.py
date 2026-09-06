from app.config.constants import COLLECTION_USERS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now

class UserRepository:
    async def create_user(self, user_data: dict) -> dict:
        user_doc = {
            "id": user_data.get("id") or generate_uuid(),
            "name": user_data["name"],
            "email": user_data["email"].lower(),
            "hashed_password": user_data.get("hashed_password", ""),
            "google_sub": user_data.get("google_sub"),
            "picture": user_data.get("picture"),
            "auth_provider": user_data.get("auth_provider", "email"),
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
                if user.get("email") == email.lower():
                    return user
            return None

    async def get_by_google_sub(self, google_sub: str) -> dict | None:
        collection = get_collection(COLLECTION_USERS)
        if collection is not None:
            return await collection.find_one({"google_sub": google_sub})
        else:
            mock_store = get_mock_collection(COLLECTION_USERS)
            for user in mock_store:
                if user.get("google_sub") == google_sub:
                    return user
            return None

    async def link_google_account(self, user_id: str, google_sub: str, picture: str | None = None) -> bool:
        update_fields = {"google_sub": google_sub}
        if picture:
            update_fields["picture"] = picture
        collection = get_collection(COLLECTION_USERS)
        if collection is not None:
            res = await collection.update_one({"id": user_id}, {"$set": update_fields})
            return res.modified_count > 0
        else:
            mock_store = get_mock_collection(COLLECTION_USERS)
            for user in mock_store:
                if user.get("id") == user_id:
                    user.update(update_fields)
                    return True
            return False

    async def get_by_id(self, user_id: str) -> dict | None:
        collection = get_collection(COLLECTION_USERS)
        if collection is not None:
            return await collection.find_one({"id": user_id})
        else:
            mock_store = get_mock_collection(COLLECTION_USERS)
            for user in mock_store:
                if user.get("id") == user_id:
                    return user
            return None

    async def save_profile(self, user_id: str, profile_data: dict) -> dict:
        doc = {"user_id": user_id, **profile_data, "updated_at": get_utc_now()}
        collection = get_collection(COLLECTION_USERS)
        if collection is not None:
            await collection.update_one({"id": user_id}, {"$set": doc})
        else:
            mock_store = get_mock_collection(COLLECTION_USERS)
            for user in mock_store:
                if user.get("id") == user_id:
                    user.update(doc)
        return doc


user_repository = UserRepository()

