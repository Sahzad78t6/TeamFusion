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
    
    # Environment & MongoDB Config
    MONGODB_URI: str = os.getenv(
        "MONGODB_URI", 
        "mongodb+srv://maximilianvfstr_db_user:8bmdwqPMjWAM4yKU@cluster0.i6pl4pa.mongodb.net/?appName=Cluster0"
    )
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "growthos")

    # JWT Security Settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "growthos_super_secret_jwt_key_2026_production_ready_32bytes"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    @property
    def SECRET_KEY(self) -> str:
        return self.JWT_SECRET

    @property
    def ALGORITHM(self) -> str:
        return self.JWT_ALGORITHM


settings = Settings()
