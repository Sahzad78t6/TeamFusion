"""Execute GrowthOS agents for conversations from the client."""
import re
from app.agents.supervisor.agent import supervisor_agent
from app.agents.user_understanding.agent import user_understanding_agent
from app.agents.planner.agent import planner_agent
from app.agents.learning_curator.agent import learning_curator_agent
from app.agents.opportunity.agent import opportunity_agent
from app.agents.reflection.agent import reflection_agent
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.opportunity_repository import opportunity_repository


def _titles(items: list[dict], limit: int = 3) -> str:
    return ", ".join(item.get("title", "Untitled") for item in items[:limit])


def _extract_goal(message: str) -> str:
    match = re.search(r"(?:want to become|want to be|become|aspire to(?: be)?|my goal is)\s+(?:a|an|the)?\s*(.+)", message, re.IGNORECASE)
    goal = (match.group(1) if match else message).strip(" .!?\n")
    return goal[:120] or "your target role"


class CopilotService:
    async def respond(self, user_id: str, message: str) -> dict:
        route = supervisor_agent.run(user_id, message)["next_step"]
        if route == "user_understanding":
            target_role = _extract_goal(message)
            identity = await user_understanding_agent.analyze_and_save(user_id, {
                "goal": target_role, "target_role": target_role,
                "skills": [], "interests": [target_role], "experience": "Beginner",
                "learning_style": "Hands-on projects",
            })
            plan = await planner_agent.create_and_save_plan(user_id, [f"Build a career as {target_role}"])
            recommendations = await learning_curator_agent.curate_and_save(user_id)
            opportunities = opportunity_agent.match(user_id, identity)
            saved_opportunities = await opportunity_repository.save_opportunities(user_id, opportunities)
            return {
                "agent": "identity_workflow",
                "message": f"Identity Twin updated: your target is {target_role}. I created a {len(plan.get('tasks', []))}-task roadmap, curated {len(recommendations.get('recommendations', []))} learning resources, and found {len(opportunities)} matching opportunities.",
                "data": {"identity": identity, "plan": plan, "recommendations": recommendations, "opportunities": saved_opportunities},
            }
        if route == "planner":
            plan = await planner_agent.create_and_save_plan(user_id, [message])
            tasks = plan.get("tasks", [])
            return {"agent": route, "message": f"Your plan is ready with {len(tasks)} focus tasks. Start with: {_titles(tasks)}.", "data": plan}
        if route == "learning_curator":
            recommendations = await learning_curator_agent.curate_and_save(user_id)
            items = recommendations.get("recommendations", [])
            return {"agent": route, "message": f"I curated {len(items)} resources for you. Top picks: {_titles(items)}.", "data": recommendations}
        if route == "opportunity":
            identity = await identity_repository.get_by_user_id(user_id) or {}
            opportunities = opportunity_agent.match(user_id, identity)
            saved = await opportunity_repository.save_opportunities(user_id, opportunities)
            return {"agent": route, "message": f"I found {len(opportunities)} matches. Best options: {_titles(opportunities)}.", "data": saved}
        if route == "reflection":
            reflection = await reflection_agent.process_and_save(user_id, {"notes": message})
            return {"agent": route, "message": f"Burnout risk: {reflection.get('risk_level', 'LOW')}. {reflection['ai_insight']}", "data": reflection}
        identity = await identity_repository.get_by_user_id(user_id) or {}
        target = identity.get("target_role") or identity.get("goal") or "your growth goal"
        return {"agent": "supervisor", "message": f"Hi! I’m ready to help with {target}. Tell me who you want to become, or ask for a plan, resources, opportunities, or a reflection.", "data": None}


copilot_service = CopilotService()