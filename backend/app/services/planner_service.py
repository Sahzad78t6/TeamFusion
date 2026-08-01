from app.database.repositories.planner_repository import planner_repository
from app.agents.planner.agent import planner_agent

class PlannerService:
    async def create_plan(self, user_id: str, plan_data: dict) -> dict:
        if not plan_data.get("tasks"):
            agent_res = planner_agent.create_plan(user_id, plan_data.get("goals", []))
            plan_data["tasks"] = agent_res["tasks"]
            plan_data["ai_feedback"] = agent_res["ai_feedback"]
        
        return await planner_repository.save_plan(user_id, plan_data)

    async def get_user_plans(self, user_id: str) -> list[dict]:
        return await planner_repository.get_plans_by_user(user_id)

planner_service = PlannerService()
