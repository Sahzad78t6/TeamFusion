from fastapi import APIRouter, Depends
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import recommendation_service
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/recommendation", tags=["Recommendations"])

@router.get("", response_model=RecommendationResponse)
async def get_recommendations(user_id: str = Depends(get_current_user_id)):
    return await recommendation_service.get_recommendations(user_id)

@router.post("/refresh", response_model=RecommendationResponse)
async def refresh_recommendations(user_id: str = Depends(get_current_user_id)):
    return await recommendation_service.refresh_recommendations(user_id)
