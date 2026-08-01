import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db_client = MongoDB()


async def connect_to_mongo() -> AsyncIOMotorDatabase:
    """
    Establish singleton connection pool to MongoDB Atlas.
    """
    logger.info("Connecting to MongoDB Atlas...")
    try:
        db_client.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            maxPoolSize=100,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000
        )
        db_client.db = db_client.client[settings.DATABASE_NAME]
        
        # Ping the database to verify connection
        await db_client.client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB Atlas database: '{settings.DATABASE_NAME}'!")
        return db_client.db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB Atlas: {e}")
        raise e


async def close_mongo_connection() -> None:
    """
    Close MongoDB connection pool on shutdown.
    """
    if db_client.client:
        logger.info("Closing MongoDB connection...")
        db_client.client.close()
        logger.info("MongoDB connection closed successfully.")


def get_database() -> AsyncIOMotorDatabase:
    """
    Database getter dependency. Returns singleton AsyncIOMotorDatabase instance.
    """
    if db_client.db is None:
        logger.warning("get_database() called but database client is not initialized.")
    return db_client.db
