import logging
from app.database.repositories.planner_repository import planner_repository
from app.agents.planner.agent import planner_agent

logger = logging.getLogger(__name__)

class PlannerService:
    async def create_plan(self, user_id: str, plan_data: dict) -> dict:
        logger.info(f"Generating learning plan for user {user_id}")
        goals = plan_data.get("goals", [])
        return await planner_agent.generate_and_store_plan(user_id, goals)

    async def get_user_plans(self, user_id: str) -> list[dict]:
        plans = await planner_repository.get_plans_by_user(user_id)
        if not plans:
            initial_plan = await planner_agent.generate_and_store_plan(user_id)
            return [initial_plan]
        return plans

    async def toggle_task_completion(self, user_id: str, task_id: str, completed: bool) -> dict:
        updated = await planner_repository.update_task_completion(user_id, task_id, completed)
        if completed:
            from app.database.repositories.analytics_repository import analytics_repository
            from app.services.activity_service import activity_service
            await analytics_repository.update_analytics(user_id, add_hours=0.5, completed_count=1)
            await activity_service.log_event(
                user_id=user_id,
                event_type="task_completed",
                metadata={"task_id": task_id, "title": f"Task {task_id}"}
            )
        return {"success": True, "updated": updated, "task_id": task_id, "completed": completed}


planner_service = PlannerService()


