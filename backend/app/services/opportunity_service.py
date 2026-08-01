from app.database.repositories.opportunity_repository import opportunity_repository
from app.agents.opportunity.agent import opportunity_agent

class OpportunityService:
    async def get_opportunities(self, user_id: str, target_role: str = "Software Architect") -> dict:
        existing = await opportunity_repository.get_by_user(user_id)
        if existing:
            return existing
        
        opps = opportunity_agent.match(user_id, target_role)
        return await opportunity_repository.save_opportunities(user_id, opps)

opportunity_service = OpportunityService()
