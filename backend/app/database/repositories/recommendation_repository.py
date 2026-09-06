from app.config.constants import COLLECTION_RECOMMENDATIONS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import get_utc_now

class RecommendationRepository:
    async def save_recommendations(
        self,
        user_id: str,
        recommendations: list[dict],
        target_role: str = "Machine Learning Engineer",
        ai_feedback: str = ""
    ) -> dict:
        doc = {
            "user_id": user_id,
            "recommendations": recommendations,
            "resources": recommendations,
            "target_role": target_role,
            "ai_feedback": ai_feedback or f"Curated {len(recommendations)} personalized resources for your learning goals.",
            "generated_at": get_utc_now()
        }
        collection = get_collection(COLLECTION_RECOMMENDATIONS)
        if collection is not None:
            await collection.update_one({"user_id": user_id}, {"$set": doc}, upsert=True)
            doc.pop('_id', None)
        else:
            mock_store = get_mock_collection(COLLECTION_RECOMMENDATIONS)
            mock_store[:] = [item for item in mock_store if item.get("user_id") != user_id]
            clean_doc = dict(doc)
            clean_doc.pop('_id', None)
            mock_store.append(clean_doc)
        return doc

    async def get_by_user(self, user_id: str) -> dict | None:
        collection = get_collection(COLLECTION_RECOMMENDATIONS)
        if collection is not None:
            doc = await collection.find_one({"user_id": user_id, "recommendations": {"$exists": True}})
            if doc:
                doc.pop('_id', None)
            return doc
        else:
            mock_store = get_mock_collection(COLLECTION_RECOMMENDATIONS)
            for item in reversed(mock_store):
                if item.get("user_id") == user_id and "recommendations" in item:
                    clean_item = dict(item)
                    clean_item.pop('_id', None)
                    return clean_item
            return None

recommendation_repository = RecommendationRepository()
