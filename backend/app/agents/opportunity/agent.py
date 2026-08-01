import logging
from app.agents.opportunity.schemas import OpportunityInput
from app.agents.opportunity.tools import find_matched_opportunities
from app.database.repositories.opportunity_repository import opportunity_repository
from app.memory.memory_manager import memory_manager

logger = logging.getLogger(__name__)

class OpportunityAgent:
    def match(self, user_id: str, identity_data: dict | None = None, raise_on_error: bool = False) -> list[dict]:
        logger.info(f"OpportunityAgent matching opportunities for user {user_id}")
        data = identity_data or {}
        role = data.get("target_role") or data.get("goal") or "AI Developer"
        skills = data.get("skills", ["Python", "AI", "FastAPI"])
        goal = data.get("goal", "")
        experience = data.get("experience", "Intermediate")

        # Pydantic validation
        validated_input = OpportunityInput(
            role=role,
            user_skills=skills,
            goal=goal,
            experience=experience
        )

        opportunities = find_matched_opportunities(
            role=validated_input.role,
            user_skills=validated_input.user_skills,
            goal=validated_input.goal,
            experience=validated_input.experience,
            raise_on_error=raise_on_error
        )

        # Mem0 call wrapped safely
        memory_manager.save_user_fact(
            user_id,
            f"Matched {len(opportunities)} career opportunities for target role '{role}'."
        )

        return opportunities

opportunity_agent = OpportunityAgent()
