import logging
from typing import Any, Dict, List, Optional
from app.database.mongodb import get_database

logger = logging.getLogger(__name__)


async def get_collection(collection_name: str):
    """
    Get a MongoDB collection from the active database.
    """
    db = get_database()
    if db is None:
        raise RuntimeError("Database connection not initialized.")
    return db[collection_name]


async def find_one(collection_name: str, filter_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Find a single document in a collection.
    """
    collection = await get_collection(collection_name)
    return await collection.find_one(filter_query)


async def find_many(collection_name: str, filter_query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
    """
    Find multiple documents in a collection.
    """
    collection = await get_collection(collection_name)
    cursor = collection.find(filter_query).limit(limit)
    return await cursor.to_list(length=limit)


async def insert_one(collection_name: str, document: Dict[str, Any]) -> str:
    """
    Insert a single document into a collection.
    """
    collection = await get_collection(collection_name)
    result = await collection.insert_one(document)
    return str(result.inserted_id)


async def update_one(collection_name: str, filter_query: Dict[str, Any], update_query: Dict[str, Any]) -> bool:
    """
    Update a single document in a collection.
    """
    collection = await get_collection(collection_name)
    result = await collection.update_one(filter_query, update_query)
    return result.modified_count > 0


async def delete_one(collection_name: str, filter_query: Dict[str, Any]) -> bool:
    """
    Delete a single document from a collection.
    """
    collection = await get_collection(collection_name)
    result = await collection.delete_one(filter_query)
    return result.deleted_count > 0
