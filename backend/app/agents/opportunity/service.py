"""Service layer for Opportunity Agent."""
import logging
from app.agents.opportunity.agent import opportunity_agent

logger = logging.getLogger(__name__)


class OpportunityService:
    async def match_opportunities(self, user_id: str) -> dict:
        """Delegate opportunity matching to the agent."""
        input_data = {"user_id": user_id}
        result = await opportunity_agent.execute(input_data)
        return result.data


opportunity_service = OpportunityService()
