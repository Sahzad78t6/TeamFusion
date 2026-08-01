import logging
from app.agents.user_understanding.agent import user_understanding_agent
from app.database.repositories.identity_repository import identity_repository
from app.memory.memory_manager import memory_manager

logger = logging.getLogger(__name__)

class OnboardingService:
    async def process_onboarding(self, user_id: str, identity_data: dict) -> dict:
        logger.info(f"Processing onboarding submission for user_id: {user_id}")
        
        # Trigger User Understanding Agent to analyze profile & persist to identity_twins collection
        identity = await user_understanding_agent.analyze_and_save(user_id, identity_data)
        
        # Save onboarding facts into Mem0 vector memory
        target = identity.get("target_role") or identity.get("goal") or "AI Leader"
        skills = identity.get("skills", [])
        fact = f"User career goal is '{target}' with skills: {', '.join(skills) if isinstance(skills, list) else skills}."
        memory_manager.save_user_fact(user_id, fact, {"type": "onboarding_profile"})

        return identity

    async def get_user_identity(self, user_id: str) -> dict | None:
        return await identity_repository.get_by_user_id(user_id)

onboarding_service = OnboardingService()
