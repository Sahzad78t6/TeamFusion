import logging
from typing import List, Dict, Any
from app.database.repositories.reflection_repo import ReflectionRepository

logger = logging.getLogger(__name__)


class ReflectionService:
    @staticmethod
    async def get_user_reflections(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return await ReflectionRepository.get_by_user_id(user_id, limit)

    @staticmethod
    async def create_reflection(data: Dict[str, Any]) -> Dict[str, Any]:
        return await ReflectionRepository.create_reflection(data)
