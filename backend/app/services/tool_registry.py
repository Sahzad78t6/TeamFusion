"""
Tool Registry — GrowthOS Supervisor Agent
Provides a controlled set of deterministic tools for reading context and executing agent actions.
Agents use services and repositories rather than raw unverified database writes.
"""
import logging
from typing import Any, Callable
from app.config.constants import COLLECTION_USERS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import get_utc_now
from app.services.activity_service import activity_service
from app.services.skill_graph_service import skill_graph_service
from app.memory.service import memory_service

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self):
        self._registry: dict[str, Callable] = {}
        self._register_default_tools()

    def register(self, name: str, func: Callable):
        self._registry[name] = func

    def get_tool(self, name: str) -> Callable | None:
        return self._registry.get(name)

    async def execute_tool(self, name: str, user_id: str, **kwargs) -> dict[str, Any]:
        """Execute a registered tool by name with safety checks."""
        func = self.get_tool(name)
        if not func:
            logger.warning(f"Tool '{name}' not found in registry.")
            return {"error": f"Tool '{name}' not found."}

        try:
            logger.info(f"Executing tool '{name}' for user '{user_id}' with args: {kwargs}")
            res = await func(user_id=user_id, **kwargs)
            return {"success": True, "result": res}
        except Exception as e:
            logger.error(f"Error executing tool '{name}': {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def list_tools(self) -> list[str]:
        return list(self._registry.keys())

    def _register_default_tools(self):
        # 1. User profile
        async def tool_get_user_profile(user_id: str, **kwargs):
            col = get_collection(COLLECTION_USERS)
            if col is not None:
                user = await col.find_one({"_id": user_id}) or await col.find_one({"id": user_id})
                if user:
                    profile = user.get("profile", {})
                    profile["user_id"] = user_id
                    profile["target_role"] = profile.get("target_role", "Machine Learning Engineer")
                    return profile
            else:
                mock = get_mock_collection(COLLECTION_USERS)
                for user in mock:
                    if user.get("id") == user_id or user.get("_id") == user_id:
                        profile = user.get("profile", {})
                        profile["user_id"] = user_id
                        return profile
            return {
                "user_id": user_id,
                "target_role": "Machine Learning Engineer",
                "skills": ["Python", "Machine Learning", "Algorithms"],
                "interests": ["AI", "Data Structures"],
                "learning_style": "hands-on",
                "available_time_per_week_hours": 5
            }
        self.register("get_user_profile", tool_get_user_profile)


        # 2. Learning activity
        async def tool_get_learning_activity(user_id: str, **kwargs):
            return await activity_service.get_user_activity(user_id, limit=20)
        self.register("get_learning_activity", tool_get_learning_activity)

        # 3. Current plan
        async def tool_get_current_plan(user_id: str, **kwargs):
            from app.agents.planner.agent import planner_agent
            return await planner_agent.get_today_plan(user_id)
        self.register("get_current_plan", tool_get_current_plan)

        # 4. Skill graph
        async def tool_get_skill_graph(user_id: str, **kwargs):
            return await skill_graph_service.get_user_skills(user_id)
        self.register("get_skill_graph", tool_get_skill_graph)

        # 5. Reflections
        async def tool_get_reflections(user_id: str, **kwargs):
            from app.agents.reflection.agent import reflection_agent
            return await reflection_agent.get_user_reflections(user_id)
        self.register("get_reflections", tool_get_reflections)

        # 6. Notifications
        async def tool_get_notifications(user_id: str, **kwargs):
            from app.agents.notification.agent import notification_agent
            return await notification_agent.get_user_notifications(user_id)
        self.register("get_notifications", tool_get_notifications)

        # 7. Create plan
        async def tool_create_plan(user_id: str, goals: list[str] | None = None, **kwargs):
            from app.agents.planner.agent import planner_agent
            return await planner_agent.generate_and_store_plan(user_id, goals=goals or ["Daily Learning Goals"])
        self.register("create_plan", tool_create_plan)

        # 8. Update task
        async def tool_update_task(user_id: str, task_id: str, completed: bool = True, **kwargs):
            from app.agents.planner.agent import planner_agent
            return await planner_agent.update_task_status(user_id, task_id, completed=completed)
        self.register("update_task", tool_update_task)

        # 9. Create notification
        async def tool_create_notification(user_id: str, title: str, message: str, category: str = "general", **kwargs):
            from app.agents.notification.agent import notification_agent
            return await notification_agent.create_notification(
                user_id=user_id, title=title, message=message, category=category
            )
        self.register("create_notification", tool_create_notification)

        # 10. Save reflection
        async def tool_save_reflection(user_id: str, reflection_text: str, mood: str = "neutral", **kwargs):
            from app.agents.reflection.agent import reflection_agent
            return await reflection_agent.process_reflection(user_id, reflection_text=reflection_text, mood=mood)
        self.register("save_reflection", tool_save_reflection)

        # 11. Search learning resources
        async def tool_search_learning_resources(user_id: str, topic: str = "", **kwargs):
            from app.agents.learning_curator.agent import learning_curator_agent
            return await learning_curator_agent.curate_resources(user_id, topic=topic)
        self.register("search_learning_resources", tool_search_learning_resources)

        # 12. Search opportunities
        async def tool_search_opportunities(user_id: str, **kwargs):
            from app.agents.opportunity.agent import opportunity_agent
            return await opportunity_agent.get_matched_opportunities(user_id)
        self.register("search_opportunities", tool_search_opportunities)

        # 13. Update memory
        async def tool_update_memory(user_id: str, memory_text: str, **kwargs):
            return memory_service.add_memory(user_id=user_id, memory_text=memory_text)
        self.register("update_memory", tool_update_memory)


tool_registry = ToolRegistry()
