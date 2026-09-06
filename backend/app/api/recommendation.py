from typing import Optional
from fastapi import APIRouter, Depends
from app.schemas.recommendation import RecommendationResponse, RefreshRecommendationRequest
from app.services.recommendation_service import recommendation_service
from app.services.activity_service import activity_service
from app.services.skill_graph_service import skill_graph_service
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/recommendation", tags=["Recommendations"])

@router.get("", response_model=RecommendationResponse)
async def get_recommendations(user_id: str = Depends(get_current_user_id)):
    return await recommendation_service.get_recommendations(user_id)

@router.post("/refresh", response_model=RecommendationResponse)
async def refresh_recommendations(
    payload: Optional[RefreshRecommendationRequest] = None,
    user_id: str = Depends(get_current_user_id)
):
    topic = payload.topic if payload and payload.topic else ""
    return await recommendation_service.refresh_recommendations(user_id, topic=topic)

@router.post("/{resource_id}/open")
async def open_resource(resource_id: str, user_id: str = Depends(get_current_user_id)):
    await activity_service.log_event(user_id, "resource_opened", {"resource_id": resource_id})
    return {"success": True, "resource_id": resource_id, "status": "opened"}

@router.post("/{resource_id}/complete")
async def complete_resource(resource_id: str, topic: str = "General", user_id: str = Depends(get_current_user_id)):
    await activity_service.log_event(user_id, "resource_completed", {"resource_id": resource_id, "topic": topic})
    await skill_graph_service.update_skill_mastery(user_id, skill_name=topic, delta_mastery=0.10, evidence=f"Completed resource {resource_id}")
    return {"success": True, "resource_id": resource_id, "status": "completed"}
