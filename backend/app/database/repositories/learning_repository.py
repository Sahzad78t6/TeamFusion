import logging
import pymongo.errors
from app.config.constants import COLLECTION_RECOMMENDATIONS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now

logger = logging.getLogger(__name__)


class LearningRepository:
    async def save_learning(self, user_id: str, data: dict) -> dict:
        """
        Persist (or overwrite) the learning bundle for a user.

        Previously used insert_one(), which caused E11000 DuplicateKeyError
        whenever the recommendations collection has a unique index on user_id
        and the curator ran more than once for the same user.

        Now uses update_one(..., upsert=True) so repeated calls for the same
        user_id are idempotent. A try/except catches the upsert insert-race
        (two concurrent first-time calls) and falls back to a plain update.
        """
        doc = {
            "user_id": user_id,
            "data": data,
            "created_at": get_utc_now(),
        }
        collection = get_collection(COLLECTION_RECOMMENDATIONS)
        if collection is not None:
            try:
                await collection.update_one(
                    {"user_id": user_id, "data": {"$exists": True}},
                    {"$set": doc},
                    upsert=True
                )
            except pymongo.errors.DuplicateKeyError:
                # Concurrent first-time upsert race: the other caller won the insert.
                # Retry as a plain update — safe because the document now exists.
                logger.warning(
                    f"DuplicateKeyError on learning upsert for user_id={user_id} "
                    f"(concurrent insert race). Retrying as plain update."
                )
                await collection.update_one(
                    {"user_id": user_id, "data": {"$exists": True}},
                    {"$set": doc}
                )
            doc.pop('_id', None)
        else:
            mock_store = get_mock_collection(COLLECTION_RECOMMENDATIONS)
            # Replace existing entry for this user_id in the mock store
            mock_store[:] = [
                item for item in mock_store
                if not (item.get("user_id") == user_id and "data" in item)
            ]
            clean_doc = dict(doc)
            clean_doc.pop('_id', None)
            mock_store.append(clean_doc)
        return doc

    async def get_by_user_id(self, user_id: str) -> dict | None:
        collection = get_collection(COLLECTION_RECOMMENDATIONS)
        if collection is not None:
            doc = await collection.find_one({"user_id": user_id, "data": {"$exists": True}})
            if doc:
                doc.pop('_id', None)
                return doc.get("data")
            return None
        else:
            mock_store = get_mock_collection(COLLECTION_RECOMMENDATIONS)
            for item in reversed(mock_store):
                if item.get("user_id") == user_id and "data" in item:
                    return item.get("data")
            return None


learning_repository = LearningRepository()
