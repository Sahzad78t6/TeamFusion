"""
User Understanding Agent — GrowthOS
Analyzes onboarding data to build a user profile and Identity Twin.
"""
import logging
from app.agents.user_understanding.tools import extract_profile_fields
from app.agents.user_understanding.schemas import UserUnderstandingInput, UserUnderstandingOutput
from app.database.repositories.user_repository import user_repository
from app.database.repositories.identity_repository import identity_repository
from app.memory.memory_manager import memory_manager
from app.schemas.models import AgentResponse, UserProfile, OnboardingInput
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


class UserUnderstandingAgent:
    """Input: onboarding data / chats. Output: User Profile & Identity Twin."""

    async def execute(self, input_data: dict) -> AgentResponse:
        """Standardized agent entry point."""
        logger.info(f"UserUnderstandingAgent.execute() called")
        user_id = input_data.get("user_id", "")
        memory_updates = []
        database_updates = []

        try:
            # Extract and normalize profile fields via LLM or deterministic fallback
            fields = await extract_profile_fields(input_data)
            profile = UserProfile(**fields)

            # Persist profile to database
            await user_repository.save_profile(user_id, profile.model_dump())
            database_updates.append("users")

            # Build identity document
            identity_data = {
                **input_data,
                **fields,
                "target_role": fields.get("target_role", input_data.get("target_role", "")),
                "skills": fields.get("skills", input_data.get("skills", [])),
            }
            identity = await identity_repository.create_or_update(user_id, identity_data)
            database_updates.append("identity_twins")

            # Store career goal as long-term memory in Mem0
            target = fields.get("target_role") or input_data.get("goal") or "AI Engineer"
            skills = fields.get("skills", [])
            fact = f"User career goal is '{target}' with skills: {', '.join(skills) if isinstance(skills, list) else skills}."
            memory_manager.save_user_fact(user_id, fact, {"type": "onboarding_profile"})
            memory_updates.append(fact)

            return AgentResponse(
                success=True,
                agent="user_understanding",
                timestamp=get_utc_now(),
                data=identity,
                memory_updates=memory_updates,
                database_updates=database_updates,
                next_recommended_agent="planner",
            )

        except Exception as e:
            logger.error(f"UserUnderstandingAgent.execute() failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                agent="user_understanding",
                timestamp=get_utc_now(),
                data={"error": str(e)},
            )

    async def build_profile(self, onboarding: OnboardingInput) -> UserProfile:
        """Legacy method — delegates to execute()."""
        result = await self.execute(onboarding.model_dump())
        fields = result.data if result.success else {}
        return UserProfile(
            target_role=fields.get("target_role", ""),
            skills=fields.get("skills", []),
            interests=fields.get("interests", []),
            learning_style=fields.get("learning_style", "hands-on"),
            available_time_per_week_hours=fields.get("available_time_per_week_hours", 5),
            aspirations=fields.get("aspirations", ""),
        )

    async def get_profile(self, user_id: str) -> UserProfile | None:
        data = await user_repository.get_by_user_id(user_id)
        return UserProfile(**data) if data else None


user_understanding_agent = UserUnderstandingAgent()
