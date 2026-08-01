from app.config.constants import (
    COLLECTION_USERS,
    COLLECTION_IDENTITIES,
    COLLECTION_PLANS,
    COLLECTION_RECOMMENDATIONS,
    COLLECTION_REFLECTIONS,
    COLLECTION_OPPORTUNITIES,
    COLLECTION_ANALYTICS,
    COLLECTION_NOTIFICATIONS
)
from app.database.mongodb import get_database, mock_db_storage

def get_collection(collection_name: str):
    db = get_database()
    if db is not None:
        return db[collection_name]
    return None

def get_mock_collection(collection_name: str) -> list[dict]:
    if collection_name not in mock_db_storage:
        mock_db_storage[collection_name] = []
    return mock_db_storage[collection_name]
