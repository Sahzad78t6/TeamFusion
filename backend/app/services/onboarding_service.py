import logging
from app.agents.user_understanding.agent import user_understanding_agent
from app.database.repositories.identity_repository import identity_repository

logger = logging.getLogger(__name__)

class OnboardingService:
    async def process_onboarding(self, user_id: str, identity_data: dict) -> dict:
        logger.info(f"Processing onboarding submission for user_id: {user_id}")
        
        # Trigger User Understanding Agent to analyze profile & persist to identity_twins collection
        identity_data["user_id"] = user_id
        result = await user_understanding_agent.execute(identity_data)
        
        return result.data if result.success else {}

    async def get_user_identity(self, user_id: str) -> dict | None:
        return await identity_repository.get_by_user_id(user_id)

onboarding_service = OnboardingService()
