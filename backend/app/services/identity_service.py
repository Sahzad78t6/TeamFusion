import logging
from typing import Optional, Dict, Any
from app.database.repositories.identity_repo import IdentityRepository

logger = logging.getLogger(__name__)


class IdentityService:
    @staticmethod
    async def get_identity_twin(user_id: str) -> Optional[Dict[str, Any]]:
        return await IdentityRepository.get_by_user_id(user_id)

    @staticmethod
    async def update_identity_twin(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await IdentityRepository.create_or_update(user_id, data)
