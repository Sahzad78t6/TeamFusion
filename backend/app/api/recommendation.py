from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.schemas.recommendation import RecommendationResponse, RefreshRecommendationRequest
from app.services.recommendation_service import recommendation_service
from app.services.activity_service import activity_service
from app.services.skill_graph_service import skill_graph_service
from app.database.repositories.learning_activity_repository import learning_activity_repository
from app.middleware.auth import get_current_user_id
from app.exceptions import (
    YouTubeQuotaExceededError,
    YouTubeApiKeyMissingError,
    YouTubeUnavailableError,
    GrowthOSError
)

router = APIRouter(prefix="/recommendation", tags=["Recommendations"])

@router.get("", response_model=RecommendationResponse)
async def get_recommendations(user_id: str = Depends(get_current_user_id)):
    return await recommendation_service.get_recommendations(user_id)

@router.post("/refresh")
async def refresh_recommendations(
    payload: Optional[RefreshRecommendationRequest] = None,
    user_id: str = Depends(get_current_user_id)
):
    topic = payload.topic if payload and payload.topic else ""
    try:
        data = await recommendation_service.refresh_recommendations(user_id, topic=topic)
        return data
    except YouTubeQuotaExceededError as e:
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": "YOUTUBE_QUOTA_EXCEEDED",
                "detail": "YouTube Data API daily search quota exceeded. Failures are transparently reported."
            }
        )
    except YouTubeApiKeyMissingError as e:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "YOUTUBE_API_KEY_MISSING",
                "detail": "YouTube Data API key is missing or not configured."
            }
        )
    except YouTubeUnavailableError as e:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "YOUTUBE_API_UNAVAILABLE",
                "detail": str(e)
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "LEARNING_CURATOR_FAILED",
                "detail": str(e)
            }
        )

@router.post("/{resource_id}/open")
async def open_resource(resource_id: str, user_id: str = Depends(get_current_user_id)):
    await learning_activity_repository.log_activity(user_id=user_id, resource_id=resource_id, action="opened", progress=10.0)
    await activity_service.log_event(user_id, "resource_opened", {"resource_id": resource_id})
    return {"success": True, "resource_id": resource_id, "status": "opened"}

@router.post("/{resource_id}/complete")
async def complete_resource(resource_id: str, topic: str = "General", user_id: str = Depends(get_current_user_id)):
    await learning_activity_repository.log_activity(user_id=user_id, resource_id=resource_id, action="completed", progress=100.0)
    await activity_service.log_event(user_id, "resource_completed", {"resource_id": resource_id, "topic": topic})
    await skill_graph_service.update_skill_mastery(user_id, skill_name=topic, delta_mastery=0.10, evidence=f"Completed resource {resource_id}")
    return {"success": True, "resource_id": resource_id, "status": "completed"}
