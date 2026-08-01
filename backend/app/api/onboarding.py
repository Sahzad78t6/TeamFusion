from fastapi import APIRouter, Depends, status
from app.middleware.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("/status", status_code=status.HTTP_200_OK)
async def onboarding_status(current_user: UserResponse = Depends(get_current_user)):
    return {"user_id": current_user.id, "completed": True}
