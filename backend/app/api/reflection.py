from fastapi import APIRouter, Depends
from app.schemas.reflection import ReflectionCreate, ReflectionResponse
from app.services.reflection_service import reflection_service
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/reflection", tags=["Reflection"])

@router.post("", response_model=ReflectionResponse)
async def create_reflection(payload: ReflectionCreate, user_id: str = Depends(get_current_user_id)):
    return await reflection_service.create_reflection(user_id, payload.model_dump())

@router.get("", response_model=list[ReflectionResponse])
async def get_reflections(user_id: str = Depends(get_current_user_id)):
    return await reflection_service.get_user_reflections(user_id)
