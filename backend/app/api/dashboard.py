from fastapi import APIRouter, Depends
from app.services.dashboard_service import dashboard_service
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("")
async def get_dashboard(user_id: str = Depends(get_current_user_id)):
    return await dashboard_service.get_dashboard_summary(user_id)
