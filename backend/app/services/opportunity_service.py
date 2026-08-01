import logging
from app.database.repositories.opportunity_repository import opportunity_repository
from app.database.repositories.identity_repository import identity_repository
from app.agents.opportunity.agent import opportunity_agent

logger = logging.getLogger(__name__)

class OpportunityService:
    async def get_opportunities(self, user_id: str) -> dict:
        existing = await opportunity_repository.get_by_user(user_id)
        if existing:
            return existing
        
        logger.info(f"Matching career opportunities for user_id: {user_id}")
        identity = await identity_repository.get_by_user_id(user_id) or {}
        matched_opps = opportunity_agent.match(user_id, identity)
        return await opportunity_repository.save_opportunities(user_id, matched_opps)

opportunity_service = OpportunityService()
