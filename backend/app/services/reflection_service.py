from app.database.repositories.reflection_repository import reflection_repository
from app.agents.reflection.agent import reflection_agent

class ReflectionService:
    async def create_reflection(self, user_id: str, data: dict) -> dict:
        processed = reflection_agent.process(
            user_id,
            data.get("mood_score", 4),
            data.get("energy_level", 4),
            data.get("notes", "")
        )
        data["ai_insight"] = processed["ai_insight"]
        return await reflection_repository.create_reflection(user_id, data)

    async def get_user_reflections(self, user_id: str) -> list[dict]:
        return await reflection_repository.get_reflections_by_user(user_id)

reflection_service = ReflectionService()
