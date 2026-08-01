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
    health
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
api_router.include_router(health.router)

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
app.include_router(health.router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs": "/docs"
    }
