from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.config import settings
from app.api.auth import router as auth_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="GrowthOS Agentic AI API — Authentication Module",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production setup can restrict to frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Authentication Router
app.include_router(auth_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Service Health Check Endpoint.
    """
    return {
        "status": "healthy",
        "service": "GrowthOS Backend API",
        "module": "Authentication"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
