from fastapi import APIRouter, Depends, status
from app.middleware.auth import get_current_user
from app.schemas.user import UserResponse
from app.services.reflection_service import ReflectionService

router = APIRouter(prefix="/reflections", tags=["Reflections"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_reflections(current_user: UserResponse = Depends(get_current_user)):
    return await ReflectionService.get_user_reflections(current_user.id)
