import logging
from app.agents.opportunity.agent import opportunity_agent
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.opportunity_repository import opportunity_repository

logger = logging.getLogger(__name__)

class OpportunityService:
    async def get_opportunities(self, user_id: str) -> dict:
        identity = await identity_repository.get_by_user_id(user_id) or {}
        opportunities = opportunity_agent.match(user_id, identity)
        saved = await opportunity_repository.save_opportunities(user_id, opportunities)
        return saved

opportunity_service = OpportunityService()
