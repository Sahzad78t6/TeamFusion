from fastapi import APIRouter, Depends
from app.services.activity_service import activity_service
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/learning/activity", tags=["Learning Activity"])

@router.get("")
async def get_activity(user_id: str = Depends(get_current_user_id)):
    events = await activity_service.get_user_activity(user_id, limit=30)
    days_inactive = await activity_service.get_days_since_last_activity(user_id)
    return {
        "user_id": user_id,
        "events": events,
        "days_since_last_activity": days_inactive
    }
