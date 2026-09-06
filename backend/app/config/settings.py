import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "GrowthOS Backend"
    ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # MongoDB
    # Credentials are supplied by the environment. Never commit connection strings.
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "growthos"

    # Security & JWT
    SECRET_KEY: str = "development-only-change-me-before-deploying"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # LLM (OpenAI & Groq)
    OPENAI_API_KEY: str = "YOUR_OPENAI_API_KEY"
    OPENAI_MODEL: str = "gpt-4o-mini"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Memory (Mem0)
    MEM0_API_KEY: str = ""

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_OAUTH_REDIRECT_URI: str = "https://teamfusion-96bi.onrender.com"
    FRONTEND_URL: str = "http://localhost:5173"

    # Search Providers (YouTube & Web Search)
    YOUTUBE_API_KEY: str = ""
    SERPER_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    GOOGLE_SEARCH_KEY: str = ""
    GOOGLE_CX: str = ""

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://team-fusion-psi.vercel.app",
        "https://teamfusion-96bi.onrender.com",
    ]

    class Config:
        env_file = (".env", "../.env")
        env_file_encoding = "utf-8"
        extra = "ignore"



settings = Settings()


