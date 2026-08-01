import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient | None = None
    db = None

db_instance = MongoDB()

# In-memory mock storage fallback when MongoDB server is not running locally
mock_db_storage: dict[str, list[dict]] = {}

async def connect_to_mongo():
    try:
        db_instance.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
        db_instance.db = db_instance.client[settings.MONGODB_DB_NAME]
        # Quick ping check
        await db_instance.client.admin.command('ping')
        logger.info(f"Connected to MongoDB at {settings.MONGODB_URL}")
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. Falling back to in-memory store mode.")
        db_instance.client = None
        db_instance.db = None

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        logger.info("Closed MongoDB connection.")

def get_database():
    return db_instance.db
