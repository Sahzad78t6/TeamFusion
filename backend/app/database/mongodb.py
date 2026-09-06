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
    COLLECTION_INSTITUTIONS,
    COLLECTION_COHORTS,
    COLLECTION_ASSESSMENTS,
    COLLECTION_ASSESSMENT_SUBMISSIONS,
    COLLECTION_LEARNING_ACTIVITY,
    COLLECTION_AGENT_RUNS,
)

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient | None = None
    db = None
    is_connected: bool = False
    connection_error: str | None = None

db_instance = MongoDB()

mock_db_storage: dict[str, list[dict]] = {}

async def init_collections_indexes():
    if db_instance.db is None:
        return
    try:
        await db_instance.db[COLLECTION_USERS].create_index("email", unique=True)
        await db_instance.db[COLLECTION_USERS].create_index("id", unique=True)
        await db_instance.db[COLLECTION_IDENTITIES].create_index("user_id", unique=True)
        await db_instance.db[COLLECTION_PLANS].create_index("user_id")
        await db_instance.db[COLLECTION_RECOMMENDATIONS].create_index("user_id", unique=True)
        await db_instance.db[COLLECTION_REFLECTIONS].create_index("user_id")
        await db_instance.db[COLLECTION_OPPORTUNITIES].create_index("user_id", unique=True)
        await db_instance.db[COLLECTION_ANALYTICS].create_index("user_id", unique=True)
        await db_instance.db[COLLECTION_NOTIFICATIONS].create_index("user_id")
        await db_instance.db[COLLECTION_INSTITUTIONS].create_index("id", unique=True)
        await db_instance.db[COLLECTION_COHORTS].create_index([("institution_id", 1), ("id", 1)], unique=True)
        await db_instance.db[COLLECTION_ASSESSMENTS].create_index([("institution_id", 1), ("cohort_id", 1)])
        await db_instance.db[COLLECTION_ASSESSMENT_SUBMISSIONS].create_index([("assessment_id", 1), ("student_id", 1)], unique=True)
        await db_instance.db[COLLECTION_LEARNING_ACTIVITY].create_index([("user_id", 1), ("resource_id", 1)])
        await db_instance.db[COLLECTION_AGENT_RUNS].create_index([("user_id", 1), ("started_at", -1)])
        logger.info("Successfully initialized MongoDB collection indexes.")
    except Exception as e:
        logger.warning(f"Index initialization warning: {e}")

async def connect_to_mongo():
    try:
        db_instance.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=3000)
        db_instance.db = db_instance.client[settings.MONGODB_DB_NAME]
        await db_instance.client.admin.command('ping')
        db_instance.is_connected = True
        db_instance.connection_error = None
        logger.info(f"Connected to MongoDB at {settings.MONGODB_URL} (db: {settings.MONGODB_DB_NAME})")
        await init_collections_indexes()
    except Exception as e:
        err_msg = str(e)
        db_instance.is_connected = False
        db_instance.connection_error = err_msg
        db_instance.client = None
        db_instance.db = None
        logger.error(
            f"CRITICAL: MongoDB connection failed ({err_msg}). "
            f"Please verify Atlas credentials or Network Access IP allowlist (0.0.0.0/0 required for dynamic IP hosts). "
            f"Falling back to in-memory store mode."
        )

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        db_instance.is_connected = False
        logger.info("Closed MongoDB connection.")

def get_database():
    return db_instance.db
