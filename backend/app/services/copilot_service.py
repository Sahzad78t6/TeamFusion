"""Execute GrowthOS agents for conversations from the client."""
from app.agents.supervisor.agent import supervisor_agent
from app.agents.planner.agent import planner_agent
from app.agents.learning_curator.agent import learning_curator_agent
from app.agents.opportunity.agent import opportunity_agent
from app.agents.reflection.agent import reflection_agent
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.opportunity_repository import opportunity_repository


class CopilotService:
    async def respond(self, user_id: str, message: str) -> dict:
        route = supervisor_agent.run(user_id, message)["next_step"]
        if route == "planner":
            plan = await planner_agent.create_and_save_plan(user_id, [message])
            return {"agent": route, "message": plan["ai_feedback"], "data": plan}
        if route == "learning_curator":
            recommendations = await learning_curator_agent.curate_and_save(user_id)
            count = len(recommendations.get("recommendations", []))
            return {"agent": route, "message": f"I curated {count} learning resources tailored to your goal.", "data": recommendations}
        if route == "opportunity":
            identity = await identity_repository.get_by_user_id(user_id) or {}
            opportunities = opportunity_agent.match(user_id, identity)
            saved = await opportunity_repository.save_opportunities(user_id, opportunities)
            return {"agent": route, "message": f"I found {len(opportunities)} opportunity matches and ranked them for you.", "data": saved}
        if route == "reflection":
            reflection = await reflection_agent.process_and_save(user_id, {"notes": message})
            return {"agent": route, "message": reflection["ai_insight"], "data": reflection}
        identity = await identity_repository.get_by_user_id(user_id) or {}
        target = identity.get("target_role") or identity.get("goal") or "your goal"
        return {"agent": "user_understanding", "message": f"Your current target is {target}. Tell me whether you want a plan, learning resources, opportunities, or a reflection check-in.", "data": identity or None}


copilot_service = CopilotService()
