from fastapi import APIRouter, Depends
from app.services.analytics_service import analytics_service
from app.middleware.auth import get_current_user_id
from app.utils.response import success_response

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("")
async def get_analytics_api(current_user_id: str = Depends(get_current_user_id)):
    data = await analytics_service.get_analytics(current_user_id)
    return success_response(data)
