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
        
        # 1. Routing
        route_result = await supervisor_agent.execute({"user_id": user_id, "message": message})
        next_agent = route_result.data.get("routed_to", "conversation")
        
        logger.info(f"Supervisor routed query to: {next_agent}")
        
        # 2. Execution
        response_data = None
        reply_message = ""
        
        try:
            if next_agent == "user_understanding":
                # For MVP, simulate passing the message as onboarding/goal update
                result = await user_understanding_agent.execute({"user_id": user_id, "goal": message})
                response_data = result.data
                reply_message = "I've updated your career profile and goals based on what you shared."
                
            elif next_agent == "planner":
                result = await planner_agent.execute({"user_id": user_id, "goals": [message]})
                response_data = result.data
                reply_message = result.data.get("ai_feedback", "Here is your updated learning roadmap.")
                
            elif next_agent == "learning_curator":
                result = await learning_curator_agent.execute({"user_id": user_id})
                response_data = result.data
                reply_message = result.data.get("ai_feedback", "I've curated some new learning resources for you.")
                
            elif next_agent == "opportunity":
                result = await opportunity_agent.execute({"user_id": user_id})
                response_data = result.data
                reply_message = result.data.get("ai_feedback", "Here are some opportunities that match your profile.")
                
            elif next_agent == "reflection":
                result = await reflection_agent.execute({"user_id": user_id, "reflection": message})
                response_data = result.data
                reply_message = result.data.get("ai_insight", "Thanks for sharing your reflection. I've logged it.")
                
            else:
                # General conversation fallback
                reply_message = llm_provider.generate(
                    prompt=message,
                    system_instruction="You are GrowthOS Copilot, a helpful AI career coach. Be concise and supportive."
                )
                
        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            if raise_on_error:
                raise
            reply_message = f"I'm sorry, I encountered an error while processing that request: {str(e)}"
            
        return CopilotResponse(
            agent=next_agent,
            message=reply_message,
            data=response_data,
        )


copilot_service = CopilotService()