import logging
from typing import List, Dict, Any
from app.database.repositories.analytics_repo import AnalyticsRepository

logger = logging.getLogger(__name__)


class AnalyticsService:
    @staticmethod
    async def log_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
        return await AnalyticsRepository.log_event(event_data)

    @staticmethod
    async def get_user_events(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        return await AnalyticsRepository.get_user_events(user_id, limit)
