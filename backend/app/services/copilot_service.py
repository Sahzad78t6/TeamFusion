"""
Copilot Service — GrowthOS
Central router for chat interactions. Uses SupervisorAgent to route queries
to the appropriate specialized agent.
"""
import logging
from app.agents.supervisor.agent import supervisor_agent
from app.agents.user_understanding.agent import user_understanding_agent
from app.agents.planner.agent import planner_agent
from app.agents.learning_curator.agent import learning_curator_agent
from app.agents.opportunity.agent import opportunity_agent
from app.agents.reflection.agent import reflection_agent
from app.schemas.copilot import CopilotResponse
from app.llm.provider import llm_provider

logger = logging.getLogger(__name__)


class CopilotService:
    async def respond(self, user_id: str, message: str, raise_on_error: bool = False) -> CopilotResponse:
        logger.info(f"Copilot received message from {user_id}: {message}")

        try:
            route_result = await supervisor_agent.execute({"user_id": user_id, "message": message})

            if not route_result.success:
                error_msg = route_result.data.get("error", "Unknown error in Supervisor")
                if raise_on_error:
                    raise RuntimeError(error_msg)
                return CopilotResponse(agent="supervisor", message=f"Supervisor encountered an error: {error_msg}")

            next_agent = route_result.data.get("routed_to", "conversation")
            summary = route_result.data.get("summary", "")
            payload = route_result.data.get("payload") or route_result.data.get("supervisor_response", {}).get("data")

            if next_agent == "conversation" or not summary:
                # Generate conversational response using LLM Provider
                llm_reply = llm_provider.generate(
                    prompt=message,
                    system_instruction="You are GrowthOS Copilot, an AI career & learning coach. Provide actionable, concise advice."
                )
                reply_message = llm_reply or summary or "How can I assist your learning journey today?"
            else:
                reply_message = summary

            return CopilotResponse(
                agent=next_agent,
                message=reply_message,
                data=payload if isinstance(payload, (dict, list)) else None
            )

        except Exception as e:
            logger.error(f"CopilotService processing failed: {e}", exc_info=True)
            if raise_on_error:
                raise
            return CopilotResponse(
                agent="supervisor",
                message=f"I'm sorry, I encountered an error while processing that request: {str(e)}"
            )


copilot_service = CopilotService()