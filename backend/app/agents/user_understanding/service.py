"""Service layer for User Understanding Agent."""
import logging
from app.agents.user_understanding.agent import user_understanding_agent

logger = logging.getLogger(__name__)


class UserUnderstandingService:
    async def process_user_onboarding(self, user_id: str, data: dict) -> dict:
        """Delegate onboarding processing to the agent."""
        data["user_id"] = user_id
        result = await user_understanding_agent.execute(data)
        return result.model_dump()


user_understanding_service = UserUnderstandingService()
