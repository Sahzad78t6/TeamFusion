from app.agents.opportunity.tools import find_matched_opportunities

class OpportunityAgent:
    def match(self, user_id: str, target_role: str) -> list[dict]:
        return find_matched_opportunities(target_role)

opportunity_agent = OpportunityAgent()
