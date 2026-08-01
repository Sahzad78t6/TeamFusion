from fastapi import APIRouter, Depends, status
from app.middleware.auth import get_current_user
from app.schemas.user import UserResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_dashboard(current_user: UserResponse = Depends(get_current_user)):
    return await DashboardService.get_dashboard_overview(current_user.id)
