from fastapi import APIRouter
from app.config.settings import settings
from app.database.mongodb import db_instance
from app.utils.response import success_response

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
async def get_health_status():
    db_connected = db_instance.is_connected and db_instance.db is not None
    db_driver = "mongodb" if db_connected else "in_memory_fallback"

    llm_configured = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY not in ("mock_groq_api_key", "YOUR_GROQ_API_KEY"))

    return success_response({
        "status": "healthy" if db_connected else "degraded",
        "app": settings.APP_NAME,
        "environment": settings.ENV,
        "database": {
            "connected": db_connected,
            "driver": db_driver,
            "database_name": settings.MONGODB_DB_NAME if db_connected else None,
            "error": db_instance.connection_error if not db_connected else None
        },
        "llm": {
            "provider": "groq",
            "model": settings.GROQ_MODEL,
            "configured": llm_configured
        }
    })
