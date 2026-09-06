from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from app.config.settings import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.middleware.cors import setup_cors
from app.middleware.logging import LoggingMiddleware

# API Routers
from app.api import (
    auth,
    onboarding,
    dashboard,
    planner,
    reflection,
    recommendation,
    opportunity,
    notification,
    copilot,
    analytics,
    skills,
    activity,
    health,
    institutions
)

from app.utils.csv_validator import validate_opportunities_csv

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate CSV dataset on startup
    validate_opportunities_csv()
    # Startup DB connection
    await connect_to_mongo()
    yield
    # Shutdown DB connection
    await close_mongo_connection()

app = FastAPI(
    title=settings.APP_NAME,
    description="GrowthOS AI Platform - Multi-agent & ML Backend Engine",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup Middleware
setup_cors(app)
app.add_middleware(LoggingMiddleware)

# Group all routers under /api
api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(onboarding.router)
api_router.include_router(dashboard.router)
api_router.include_router(planner.router)
api_router.include_router(reflection.router)
api_router.include_router(recommendation.router)
api_router.include_router(opportunity.router)
api_router.include_router(notification.router)
api_router.include_router(copilot.router)
api_router.include_router(analytics.router)
api_router.include_router(skills.router)
api_router.include_router(activity.router)
api_router.include_router(health.router)
api_router.include_router(institutions.router)

app.include_router(api_router)

# Also expose direct root routes for backward compatibility / docs convenience
app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(dashboard.router)
app.include_router(planner.router)
app.include_router(reflection.router)
app.include_router(recommendation.router)
app.include_router(opportunity.router)
app.include_router(notification.router)
app.include_router(copilot.router)
app.include_router(analytics.router)
app.include_router(skills.router)
app.include_router(activity.router)
app.include_router(health.router)
app.include_router(institutions.router)



import urllib.parse
from fastapi.responses import RedirectResponse
from app.services.auth_service import auth_service

@app.get("/", tags=["Root"])
async def root(code: str | None = None, state: str | None = None, error: str | None = None):
    # Process Google OAuth Callback ONLY when authorization code or OAuth error is present
    if code or error:
        frontend_base = settings.FRONTEND_URL.rstrip("/") + "/login"
        
        if error:
            error_clean = urllib.parse.quote(f"Google OAuth Error: {error}")
            return RedirectResponse(url=f"{frontend_base}?auth_error={error_clean}", status_code=302)

        try:
            redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
            res = await auth_service.handle_google_code_exchange(code=code, redirect_uri=redirect_uri)
            
            token = res.get("access_token", "")
            refresh_token = res.get("refresh_token", "")
            user_id = res.get("user", {}).get("id", "")
            user_name = urllib.parse.quote(res.get("user", {}).get("name", ""))
            user_email = urllib.parse.quote(res.get("user", {}).get("email", ""))

            redirect_target = (
                f"{frontend_base}?access_token={token}&refresh_token={refresh_token}"
                f"&user_id={user_id}&user_name={user_name}&user_email={user_email}"
            )
            return RedirectResponse(url=redirect_target, status_code=302)
        except Exception as e:
            error_clean = urllib.parse.quote(str(e))
            return RedirectResponse(url=f"{frontend_base}?auth_error={error_clean}", status_code=302)

    # Standard Render Health & Status Response when no OAuth parameters exist
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs": "/docs"
    }

