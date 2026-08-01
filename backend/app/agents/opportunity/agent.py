"""
Opportunity Agent — GrowthOS
Matches users with career opportunities based on their Identity Twin.
"""
import logging
from app.agents.opportunity.tools import match_opportunities
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.opportunity_repository import opportunity_repository
from app.schemas.models import AgentResponse, OpportunityBundle
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


class OpportunityAgent:
    """Input: Identity Twin. Output: Matched career opportunities."""

    async def execute(self, input_data: dict) -> AgentResponse:
        """Standardized agent entry point."""
        logger.info(f"OpportunityAgent.execute() called")
        user_id = input_data.get("user_id", "")
        
        try:
            identity = await identity_repository.get_by_user_id(user_id) or {}
            
            # Match opportunities via LLM or fallback
            matched_opps = await match_opportunities(identity)
            
            bundle = OpportunityBundle(
                opportunities=matched_opps,
                ai_feedback="Here are some opportunities aligned with your current skills and goals."
            )
            
            bundle_doc = {
                "user_id": user_id,
                **bundle.model_dump()
            }
            await opportunity_repository.save_opportunities(user_id, bundle_doc)

            return AgentResponse(
                success=True,
                agent="opportunity",
                timestamp=get_utc_now(),
                data=bundle_doc,
                database_updates=["opportunities"],
                next_recommended_agent="conversation",
            )
        except Exception as e:
            logger.error(f"OpportunityAgent.execute() failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                agent="opportunity",
                timestamp=get_utc_now(),
                data={"error": str(e)},
            )

    async def match(self, user_id: str, identity: dict) -> dict:
        """Legacy method — delegates to execute()."""
        result = await self.execute({"user_id": user_id})
        return result.data if result.success else {}


opportunity_agent = OpportunityAgent()
