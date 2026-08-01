from fastapi import APIRouter, Depends, status
from app.middleware.auth import get_current_user
from app.schemas.user import UserResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_recommendations(current_user: UserResponse = Depends(get_current_user)):
    return await RecommendationService.get_user_recommendations(current_user.id)
