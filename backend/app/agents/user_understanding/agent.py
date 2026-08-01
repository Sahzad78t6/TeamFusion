import logging
from app.agents.user_understanding.schemas import UserOnboardingInput, IdentityTwinAnalysisOutput
from app.agents.user_understanding.tools import generate_identity_twin_analysis
from app.database.repositories.identity_repository import identity_repository
from app.memory.memory_manager import memory_manager

logger = logging.getLogger(__name__)

class UserUnderstandingAgent:
    async def analyze_and_save(self, user_id: str, onboarding_data: dict, raise_on_error: bool = False) -> dict:
        logger.info(f"UserUnderstandingAgent analyzing profile for user {user_id}")
        
        # Pydantic validation before any Groq or Mongo call
        validated_input = UserOnboardingInput(**onboarding_data)
        validated_dict = validated_input.model_dump()

        analysis = generate_identity_twin_analysis(validated_dict, raise_on_error=raise_on_error)
        
        merged_data = {
            **validated_dict,
            "identity_score": analysis.get("identity_score", 88.0),
            "identity_drift_percentage": analysis.get("identity_drift_percentage", 12.0),
            "key_strengths": analysis.get("key_strengths", validated_dict.get("skills", [])),
            "skill_gaps": analysis.get("skill_gaps", ["System Architecture"]),
            "strategic_insight": analysis.get("strategic_insight", "Profile processed successfully."),
            "degraded": analysis.get("degraded", False),
            "reason": analysis.get("reason")
        }
        
        saved_identity = await identity_repository.create_or_update(user_id, merged_data)

        # Mem0 call wrapped safely
        goal = validated_input.goal or validated_input.target_role
        skills_str = ", ".join(validated_input.skills) if validated_input.skills else "General"
        memory_manager.save_user_fact(
            user_id,
            f"User career goal is '{goal}' with skills: {skills_str}."
        )

        return saved_identity

user_understanding_agent = UserUnderstandingAgent()
