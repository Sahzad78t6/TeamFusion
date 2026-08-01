import logging
from app.agents.user_understanding.agent import user_understanding_agent

logger = logging.getLogger(__name__)

class UserUnderstandingService:
    async def process_user_onboarding(self, user_id: str, data: dict) -> dict:
        return await user_understanding_agent.analyze_and_save(user_id, data)

user_understanding_service = UserUnderstandingService()
