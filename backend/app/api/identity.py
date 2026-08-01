from fastapi import APIRouter, Depends, status
from app.middleware.auth import get_current_user
from app.schemas.user import UserResponse
from app.services.identity_service import IdentityService

router = APIRouter(prefix="/identity", tags=["Identity Twin"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_identity(current_user: UserResponse = Depends(get_current_user)):
    return await IdentityService.get_identity_twin(current_user.id)
