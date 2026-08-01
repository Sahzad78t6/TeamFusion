from typing import Any

try:
    from bson import ObjectId
except ImportError:  # pragma: no cover - bson is provided by pymongo in production
    ObjectId = ()


def clean_for_api(value: Any) -> Any:
    """Remove database-only BSON fields before FastAPI serializes a response."""
    if isinstance(value, dict):
        return {key: clean_for_api(item) for key, item in value.items() if key != "_id"}
    if isinstance(value, list):
        return [clean_for_api(item) for item in value]
    if ObjectId and isinstance(value, ObjectId):
        return str(value)
    return value