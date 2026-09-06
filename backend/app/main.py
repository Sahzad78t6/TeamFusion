import logging
import urllib.parse
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import ResponseValidationError

logger = logging.getLogger(__name__)

from app.config.settings import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.middleware.cors import setup_cors
from app.middleware.logging import LoggingMiddleware
from app.services.auth_service import auth_service

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

@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    logger.error(f"Response serialization error on {request.url}: {exc.errors()}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Backend response serialization error.", "errors": [str(e) for e in exc.errors()]}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred while processing the request.", "error": str(exc)}
    )

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


@app.get("/", tags=["Root"])
async def root(code: str | None = None, state: str | None = None, error: str | None = None):
    # Process Google OAuth Callback ONLY when authorization code or OAuth error is present
    if code or error:
        # Determine target frontend domain strictly by state & environment settings
        if state and state.startswith("dev") and settings.ENV == "development":
            frontend_domain = "http://localhost:5173"
        else:
            frontend_domain = settings.FRONTEND_URL.rstrip("/")
            if "localhost" in frontend_domain:
                frontend_domain = "https://team-fusion-psi.vercel.app"
        
        if error:
            error_clean = urllib.parse.quote(f"Google OAuth Error: {error}")
            return RedirectResponse(url=f"{frontend_domain}/login?auth_error={error_clean}", status_code=302)

        try:
            redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
            res = await auth_service.handle_google_code_exchange(code=code, redirect_uri=redirect_uri)
            
            # Check user onboarding state
            user_info = res.get("user", {})
            target_route = "/onboarding" if user_info.get("onboarding_completed") is False else "/dashboard"

            # Issue single-use 60-second exchange ticket
            ticket = auth_service.create_auth_ticket(res)

            redirect_target = f"{frontend_domain}{target_route}?ticket={ticket}"
            return RedirectResponse(url=redirect_target, status_code=302)
        except Exception as e:
            error_clean = urllib.parse.quote(str(e))
            return RedirectResponse(url=f"{frontend_domain}/login?auth_error={error_clean}", status_code=302)

    # Standard Render Health & Status Response when no OAuth parameters exist
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs": "/docs"
    }
