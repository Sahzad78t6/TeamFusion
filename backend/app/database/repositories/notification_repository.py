from app.config.constants import COLLECTION_NOTIFICATIONS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now

class NotificationRepository:
    async def create_notification(self, user_id: str, title: str, message: str, notif_type: str = "info") -> dict:
        doc = {
            "id": generate_uuid(),
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notif_type,
            "read": False,
            "created_at": get_utc_now()
        }
        collection = get_collection(COLLECTION_NOTIFICATIONS)
        if collection is not None:
            await collection.insert_one(doc)
        else:
            mock_store = get_mock_collection(COLLECTION_NOTIFICATIONS)
            mock_store.append(doc)
        return doc

    async def save_notifications(self, user_id: str, notifications: list[dict]) -> list[dict]:
        collection = get_collection(COLLECTION_NOTIFICATIONS)
        saved = []
        for notif in notifications:
            doc = {
                "id": notif.get("id") or generate_uuid(),
                "user_id": user_id,
                "title": notif.get("title", "GrowthOS Alert"),
                "message": notif.get("message", ""),
                "type": notif.get("type", "info"),
                "read": notif.get("read", False),
                "created_at": notif.get("created_at") or get_utc_now()
            }
            if collection is not None:
                await collection.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)
            else:
                mock_store = get_mock_collection(COLLECTION_NOTIFICATIONS)
                mock_store[:] = [n for n in mock_store if n.get("id") != doc["id"]]
                mock_store.append(doc)
            saved.append(doc)
        return saved

    async def get_by_user(self, user_id: str) -> list[dict]:
        collection = get_collection(COLLECTION_NOTIFICATIONS)
        if collection is not None:
            cursor = collection.find({"user_id": user_id}).sort("created_at", -1)
            return await cursor.to_list(length=100)
        else:
            mock_store = get_mock_collection(COLLECTION_NOTIFICATIONS)
            return [n for n in mock_store if n.get("user_id") == user_id]

    async def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        collection = get_collection(COLLECTION_NOTIFICATIONS)
        if collection is not None:
            res = await collection.update_one({"user_id": user_id, "id": notification_id}, {"$set": {"read": True}})
            return res.modified_count > 0
        else:
            mock_store = get_mock_collection(COLLECTION_NOTIFICATIONS)
            for n in mock_store:
                if n.get("user_id") == user_id and n.get("id") == notification_id:
                    n["read"] = True
                    return True
            return False

notification_repository = NotificationRepository()
