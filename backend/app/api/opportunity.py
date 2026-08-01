from fastapi import APIRouter, Depends
from app.schemas.opportunity import OpportunityResponse
from app.services.opportunity_service import opportunity_service
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/opportunity", tags=["Opportunities"])

@router.get("", response_model=OpportunityResponse)
async def get_opportunities(user_id: str = Depends(get_current_user_id)):
    return await opportunity_service.get_opportunities(user_id)
