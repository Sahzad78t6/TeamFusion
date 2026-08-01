from app.config.constants import COLLECTION_RECOMMENDATIONS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import get_utc_now

class RecommendationRepository:
    async def save_recommendations(self, user_id: str, recommendations: list[dict]) -> dict:
        doc = {
            "user_id": user_id,
            "recommendations": recommendations,
            "generated_at": get_utc_now()
        }
        collection = get_collection(COLLECTION_RECOMMENDATIONS)
        if collection is not None:
            await collection.update_one({"user_id": user_id}, {"$set": doc}, upsert=True)
        else:
            mock_store = get_mock_collection(COLLECTION_RECOMMENDATIONS)
            mock_store[:] = [item for item in mock_store if item["user_id"] != user_id]
            mock_store.append(doc)
        return doc

    async def get_by_user(self, user_id: str) -> dict | None:
        collection = get_collection(COLLECTION_RECOMMENDATIONS)
        if collection is not None:
            return await collection.find_one({"user_id": user_id})
        else:
            mock_store = get_mock_collection(COLLECTION_RECOMMENDATIONS)
            for item in mock_store:
                if item["user_id"] == user_id:
                    return item
            return None

recommendation_repository = RecommendationRepository()
