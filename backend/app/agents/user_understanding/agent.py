import logging
from app.agents.user_understanding.tools import generate_identity_twin_analysis
from app.database.repositories.identity_repository import identity_repository

logger = logging.getLogger(__name__)

class UserUnderstandingAgent:
    async def analyze_and_save(self, user_id: str, onboarding_data: dict) -> dict:
        logger.info(f"UserUnderstandingAgent analyzing profile for user {user_id}")
        analysis = generate_identity_twin_analysis(onboarding_data)
        
        merged_data = {
            **onboarding_data,
            "identity_score": analysis.get("identity_score", 88.0),
            "identity_drift_percentage": analysis.get("identity_drift_percentage", 12.0),
            "key_strengths": analysis.get("key_strengths", onboarding_data.get("skills", [])),
            "skill_gaps": analysis.get("skill_gaps", ["Distributed Systems"]),
            "strategic_insight": analysis.get("strategic_insight", "Profile processed successfully.")
        }
        
        saved_identity = await identity_repository.create_or_update(user_id, merged_data)
        return saved_identity

user_understanding_agent = UserUnderstandingAgent()
