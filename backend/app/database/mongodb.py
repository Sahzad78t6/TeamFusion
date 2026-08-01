import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from app.config.constants import (
    COLLECTION_USERS,
    COLLECTION_IDENTITIES,
    COLLECTION_PLANS,
    COLLECTION_RECOMMENDATIONS,
    COLLECTION_REFLECTIONS,
    COLLECTION_OPPORTUNITIES,
    COLLECTION_ANALYTICS,
    COLLECTION_NOTIFICATIONS,
)

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient | None = None
    db = None

db_instance = MongoDB()

mock_db_storage: dict[str, list[dict]] = {}

async def init_collections_indexes():
    if db_instance.db is None:
        return
    try:
        # Create indexes asynchronously for performance and data integrity
        await db_instance.db[COLLECTION_USERS].create_index("email", unique=True)
        await db_instance.db[COLLECTION_USERS].create_index("id", unique=True)
        await db_instance.db[COLLECTION_IDENTITIES].create_index("user_id", unique=True)
        await db_instance.db[COLLECTION_PLANS].create_index("user_id")
        await db_instance.db[COLLECTION_RECOMMENDATIONS].create_index("user_id", unique=True)
        await db_instance.db[COLLECTION_REFLECTIONS].create_index("user_id")
        await db_instance.db[COLLECTION_OPPORTUNITIES].create_index("user_id", unique=True)
        await db_instance.db[COLLECTION_ANALYTICS].create_index("user_id", unique=True)
        await db_instance.db[COLLECTION_NOTIFICATIONS].create_index("user_id")
        logger.info("Successfully initialized MongoDB collection indexes.")
    except Exception as e:
        logger.warning(f"Index initialization warning: {e}")

async def connect_to_mongo():
    try:
        db_instance.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
        db_instance.db = db_instance.client[settings.MONGODB_DB_NAME]
        await db_instance.client.admin.command('ping')
        logger.info(f"Connected to MongoDB at {settings.MONGODB_URL} (db: {settings.MONGODB_DB_NAME})")
        await init_collections_indexes()
    except Exception as e:
        logger.warning(f"MongoDB connection failed ({e}). Falling back to in-memory store mode.")
        db_instance.client = None
        db_instance.db = None

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        logger.info("Closed MongoDB connection.")

def get_database():
    return db_instance.db
