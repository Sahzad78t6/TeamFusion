from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings

def setup_cors(app):
    allowed_origins = set(settings.CORS_ORIGINS)
    # Ensure production and dev origins are always allowed
    allowed_origins.add("https://team-fusion-psi.vercel.app")
    allowed_origins.add("https://teamfusion-96bi.onrender.com")
    allowed_origins.add("http://localhost:5173")
    allowed_origins.add("http://localhost:3000")
    allowed_origins.add("http://127.0.0.1:5173")
    allowed_origins.add("http://127.0.0.1:3000")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
