import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseConfig:
    URL: str = settings.MONGODB_URL
    DB_NAME: str = settings.MONGODB_DB_NAME
    
    @classmethod
    def get_db_info(cls) -> dict:
        return {
            "url": cls.URL,
            "db_name": cls.DB_NAME
        }

db_config = DatabaseConfig()
