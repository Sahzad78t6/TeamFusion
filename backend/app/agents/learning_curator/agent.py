import logging
from app.agents.learning_curator.schemas import LearningCuratorInput
from app.agents.learning_curator.tools import generate_ai_recommendations
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.recommendation_repository import recommendation_repository
from app.memory.memory_manager import memory_manager

logger = logging.getLogger(__name__)

class LearningCuratorAgent:
    async def curate_and_save(self, user_id: str, raise_on_error: bool = False) -> dict:
        logger.info(f"LearningCuratorAgent curating resources for user {user_id}")
        identity = await identity_repository.get_by_user_id(user_id) or {}

        target_role = identity.get("target_role") or identity.get("goal") or "AI Specialist"
        skills = identity.get("skills", ["Python", "FastAPI"])
        learning_style = identity.get("learning_style", "Hands-on projects")

        # Pydantic validation before calling Groq or Mongo
        validated_input = LearningCuratorInput(
            target_role=target_role,
            skills=skills,
            learning_style=learning_style
        )

        recs = generate_ai_recommendations(
            target_role=validated_input.target_role,
            skills=validated_input.skills,
            learning_style=validated_input.learning_style,
            raise_on_error=raise_on_error
        )

        saved_doc = await recommendation_repository.save_recommendations(user_id, recs)

        # Mem0 call wrapped safely
        memory_manager.save_user_fact(
            user_id,
            f"Curated {len(recs)} learning resources for {target_role}."
        )

        return saved_doc

learning_curator_agent = LearningCuratorAgent()
