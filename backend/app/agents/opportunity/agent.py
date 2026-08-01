from app.agents.opportunity.tools import find_matched_opportunities

class OpportunityAgent:
    def match(self, user_id: str, identity_data: dict | None = None) -> list[dict]:
        data = identity_data or {}
        role = data.get("target_role") or data.get("goal") or "AI Developer"
        skills = data.get("skills", ["Python", "AI", "FastAPI"])
        goal = data.get("goal", "")
        experience = data.get("experience", "Intermediate")

        return find_matched_opportunities(role=role, user_skills=skills, goal=goal, experience=experience)

opportunity_agent = OpportunityAgent()
