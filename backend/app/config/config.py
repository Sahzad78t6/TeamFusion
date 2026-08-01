import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file explicitly
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

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

    # Supabase Credentials
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://episyanpewjwwcvgjlyg.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "sb_publishable_-ZBmRlt-Xt90B7SFVHNbjw_AvR2AoWr")


settings = Settings()
