"""
Supervisor Agent — GrowthOS
Central orchestrator for multi-agent reasoning, context retrieval, tool invocation, and structured response contracts.
"""
import logging
import time
from typing import Any
from app.agents.supervisor.router import route_next_agent
from app.schemas.models import AgentResponse, SupervisorResponse
from app.services.tool_registry import tool_registry
from app.services.agent_observability import observability_service
from app.memory.service import memory_service
from app.ml.service import ml_service
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Orchestrates specialized agents and tools over user context."""

    async def execute(self, input_data: dict) -> AgentResponse:
        start_time = time.time()
        user_id = input_data.get("user_id", "demo_user")
        query = input_data.get("message", "").strip()

        logger.info(f"SupervisorAgent processing query for {user_id}: '{query}'")

        try:
            # 1. Context Retrieval
            user_profile = await tool_registry.execute_tool("get_user_profile", user_id=user_id)
            current_plan = await tool_registry.execute_tool("get_current_plan", user_id=user_id)
            skills = await tool_registry.execute_tool("get_skill_graph", user_id=user_id)
            memories = memory_service.get_memories(user_id=user_id)
            risk_info = await ml_service.predict_risk(user_id)

            target_agent = route_next_agent(query)
            tool_calls = []

            # Destructive / High-risk action detection
            requires_confirmation = any(
                w in query.lower() for w in ["delete my entire", "erase history", "reset account", "clear all data"]
            )

            response_payload: dict[str, Any] = {}
            intent = f"handle_{target_agent}"
            action = "route"
            result_summary = ""

            # Specialized Agent Execution Flow
            if target_agent == "planner":
                intent = "create_or_fetch_plan"
                action = "generate_daily_plan"
                tool_calls.append("create_plan")
                plan_res = await tool_registry.execute_tool("create_plan", user_id=user_id)
                response_payload = plan_res.get("result", {})
                result_summary = "I have reviewed your goals and generated an updated daily learning plan in your Daily Planner."

            elif target_agent == "learning_curator":
                intent = "curate_learning_resources"
                action = "search_learning_resources"
                tool_calls.append("search_learning_resources")
                curate_res = await tool_registry.execute_tool("search_learning_resources", user_id=user_id)
                response_payload = curate_res.get("result", {})
                result_summary = "I've curated personalized learning resources targeting your current skill gaps."

            elif target_agent == "opportunity":
                intent = "match_opportunities"
                action = "search_opportunities"
                tool_calls.append("search_opportunities")
                opp_res = await tool_registry.execute_tool("search_opportunities", user_id=user_id)
                response_payload = opp_res.get("result", {})
                result_summary = "Here are career and project opportunities matched to your target role and skills."

            elif target_agent == "reflection":
                intent = "save_and_analyze_reflection"
                action = "save_reflection"
                tool_calls.append("save_reflection")
                ref_res = await tool_registry.execute_tool("save_reflection", user_id=user_id, reflection_text=query)
                response_payload = ref_res.get("result", {})
                result_summary = "Thank you for sharing your reflection. I've logged your insights and updated your profile memory."

            else:
                intent = "conversational_guidance"
                action = "general_reply"
                result_summary = "GrowthOS Supervisor ready to help you optimize your learning roadmap."
                response_payload = {
                    "memories": memories,
                    "risk_indicator": risk_info,
                    "target_role": user_profile.get("result", {}).get("target_role", "Machine Learning Engineer")
                }

            supervisor_contract = SupervisorResponse(
                intent=intent,
                agent=target_agent,
                action=action,
                result=result_summary,
                data=response_payload,
                confidence=0.95,
                requires_confirmation=requires_confirmation
            )

            duration_ms = (time.time() - start_time) * 1000.0

            # Observability logging
            await observability_service.log_run(
                user_id=user_id,
                selected_agent=target_agent,
                tool_calls=tool_calls,
                duration_ms=duration_ms,
                success=True,
                supervisor="supervisor"
            )

            return AgentResponse(
                success=True,
                agent="supervisor",
                timestamp=get_utc_now(),
                data={
                    "routed_to": target_agent,
                    "supervisor_response": supervisor_contract.model_dump(),
                    "payload": response_payload,
                    "summary": result_summary
                },
                next_recommended_agent=target_agent
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000.0
            logger.error(f"SupervisorAgent execution error: {e}", exc_info=True)
            await observability_service.log_run(
                user_id=user_id,
                selected_agent="supervisor_error",
                tool_calls=[],
                duration_ms=duration_ms,
                success=False,
                error=str(e)
            )
            return AgentResponse(
                success=False,
                agent="supervisor",
                timestamp=get_utc_now(),
                data={"error": str(e)}
            )

    async def route(self, user_id: str, message: str) -> str:
        res = await self.execute({"user_id": user_id, "message": message})
        return res.data.get("routed_to", "conversation") if res.success else "conversation"

    def run(self, user_id: str, message: str) -> dict:
        next_agent = route_next_agent(message)
        return {"next_step": next_agent}


supervisor_agent = SupervisorAgent()
