from fastapi import APIRouter, Depends
from app.schemas.notification import NotificationResponse
from app.services.notification_service import notification_service
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/notification", tags=["Notifications"])

@router.get("", response_model=NotificationResponse)
async def get_notifications(user_id: str = Depends(get_current_user_id)):
    return await notification_service.get_user_notifications(user_id)
