from fastapi import APIRouter
from app.config.settings import settings
from app.utils.response import success_response

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
async def get_health_status():
    return success_response({
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.ENV
    })
