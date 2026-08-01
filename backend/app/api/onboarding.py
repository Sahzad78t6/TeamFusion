from fastapi import APIRouter, Depends
from app.schemas.identity import IdentityCreate, IdentityResponse
from app.services.onboarding_service import onboarding_service
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/onboarding", tags=["Onboarding & Identity"])

@router.post("", response_model=IdentityResponse)
async def submit_onboarding(payload: IdentityCreate, user_id: str = Depends(get_current_user_id)):
    return await onboarding_service.process_onboarding(user_id, payload.model_dump())

@router.get("/identity", response_model=IdentityResponse | None)
async def get_identity(user_id: str = Depends(get_current_user_id)):
    res = await onboarding_service.get_user_identity(user_id)
    return res
