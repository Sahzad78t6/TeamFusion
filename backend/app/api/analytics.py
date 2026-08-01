from fastapi import APIRouter, Depends, status
from app.middleware.auth import get_current_user
from app.schemas.user import UserResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_analytics(current_user: UserResponse = Depends(get_current_user)):
    return await AnalyticsService.get_user_events(current_user.id)
