"""
Supervisor Agent — GrowthOS
Skeleton router agent. Determines the next agent to invoke based on user input.
"""
import logging
from app.agents.supervisor.router import route_next_agent
from app.schemas.models import AgentResponse
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Input: User query. Output: Next agent routing."""

    async def execute(self, input_data: dict) -> AgentResponse:
        """Standardized agent entry point."""
        logger.info(f"SupervisorAgent.execute() called")
        query = input_data.get("message", "")
        
        try:
            next_agent = route_next_agent(query)
            
            return AgentResponse(
                success=True,
                agent="supervisor",
                timestamp=get_utc_now(),
                data={"routed_to": next_agent},
                next_recommended_agent=next_agent,
            )
        except Exception as e:
            logger.error(f"SupervisorAgent.execute() failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                agent="supervisor",
                timestamp=get_utc_now(),
                data={"error": str(e)},
            )

    async def route(self, user_id: str, message: str) -> str:
        """Legacy method — delegates to execute()."""
        result = await self.execute({"user_id": user_id, "message": message})
        return result.data.get("routed_to", "conversation") if result.success else "conversation"


supervisor_agent = SupervisorAgent()
