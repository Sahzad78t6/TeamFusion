import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_client = MongoDB()

async def connect_to_mongo():
    logger.info("Connecting to MongoDB Atlas...")
    try:
        db_client.client = AsyncIOMotorClient(settings.MONGODB_URI)
        db_client.db = db_client.client[settings.DATABASE_NAME]
        
        # Ping the database to verify connection
        await db_client.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas!")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    if db_client.client:
        logger.info("Closing MongoDB connection...")
        db_client.client.close()
        logger.info("MongoDB connection closed.")

def get_database():
    return db_client.db
