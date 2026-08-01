from fastapi import APIRouter, Depends
from app.schemas.planner import PlanCreate, PlanResponse
from app.services.planner_service import planner_service
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/planner", tags=["Planner"])

@router.post("", response_model=PlanResponse)
async def create_plan(payload: PlanCreate, user_id: str = Depends(get_current_user_id)):
    return await planner_service.create_plan(user_id, payload.model_dump())

@router.get("", response_model=list[PlanResponse])
async def get_plans(user_id: str = Depends(get_current_user_id)):
    return await planner_service.get_user_plans(user_id)
