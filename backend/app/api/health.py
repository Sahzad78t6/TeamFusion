from fastapi import APIRouter
from app.config.settings import settings
from app.database.mongodb import db_instance
from app.utils.response import success_response

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
async def get_health_status():
    db_connected = db_instance.is_connected and db_instance.db is not None
    db_driver = "mongodb" if db_connected else "in_memory_fallback"

    # NOTE: Runtime LLM path uses OPENAI_API_KEY (not GROQ_API_KEY).
    # A previous Groq→OpenAI migration left GROQ checks here — now corrected.
    llm_configured = bool(
        settings.OPENAI_API_KEY
        and settings.OPENAI_API_KEY not in ("YOUR_OPENAI_API_KEY", "")
    )

    search_configured = {
        "youtube": bool(
            settings.YOUTUBE_API_KEY
            and not settings.YOUTUBE_API_KEY.startswith("your_")
            and settings.YOUTUBE_API_KEY != ""
        ),
        "serper": bool(
            settings.SERPER_API_KEY
            and not settings.SERPER_API_KEY.startswith("your_")
            and settings.SERPER_API_KEY != ""
        ),
        "tavily": bool(
            settings.TAVILY_API_KEY
            and not settings.TAVILY_API_KEY.startswith("your_")
            and settings.TAVILY_API_KEY != ""
        ),
        "google_cse": bool(
            settings.GOOGLE_SEARCH_KEY
            and settings.GOOGLE_CX
            and settings.GOOGLE_SEARCH_KEY != ""
            and settings.GOOGLE_CX != ""
        ),
    }

    any_search_configured = any(search_configured.values())

    # Overall status: healthy only if DB is connected.
    # "degraded" if no LLM or search keys — AI features will fall back.
    if not db_connected:
        status = "unhealthy"
    elif not llm_configured and not any_search_configured:
        status = "degraded"
    else:
        status = "healthy"

    return success_response({
        "status": status,
        "app": settings.APP_NAME,
        "environment": settings.ENV,
        "database": {
            "connected": db_connected,
            "driver": db_driver,
            "database_name": settings.MONGODB_DB_NAME if db_connected else None,
            "error": db_instance.connection_error if not db_connected else None
        },
        "integrations": {
            "llm": {
                "provider": "openai",
                "model": settings.OPENAI_MODEL,
                "configured": llm_configured,
                # When False, ALL agent calls that use the LLM will fall back to
                # deterministic heuristics. Set OPENAI_API_KEY in Render env vars.
                "warning": None if llm_configured else "OPENAI_API_KEY is missing or placeholder — all LLM calls will use deterministic fallbacks"
            },
            "search": {
                **search_configured,
                "any_configured": any_search_configured,
                # When all False, curator live-search will fail (no DuckDuckGo on cloud hosts).
                "warning": None if any_search_configured else "No search provider keys set — curator live-search will return 0 results on cloud hosts like Render"
            }
        }
    })
