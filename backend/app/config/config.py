import os

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "GrowthOS"
    API_V1_STR: str = "/api"
    
    # JWT Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "growthos_super_secret_jwt_key_2026_change_in_production_32bytes")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 Minutes Expiry
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # 7 Days Expiry

    # Supabase Credentials (loaded from environment or .env)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://episyanpewjwwcvgjlyg.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_SERVICE_OR_ANON_KEY")


settings = Settings()
