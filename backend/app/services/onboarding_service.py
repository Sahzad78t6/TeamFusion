from app.database.repositories.identity_repository import identity_repository
from app.memory.memory_manager import memory_manager

class OnboardingService:
    async def process_onboarding(self, user_id: str, identity_data: dict) -> dict:
        identity = await identity_repository.create_or_update(user_id, identity_data)
        
        # Retain onboarding context in Mem0 memory
        fact = f"User target role is '{identity['target_role']}' with skills: {', '.join(identity['skills'])}."
        memory_manager.save_user_fact(user_id, fact, {"type": "onboarding_profile"})

        return identity

    async def get_user_identity(self, user_id: str) -> dict | None:
        return await identity_repository.get_by_user_id(user_id)

onboarding_service = OnboardingService()
