from app.agents.supervisor.router import route_next_agent
from app.llm.gemini import gemini_llm

class SupervisorAgent:
    def run(self, user_id: str, prompt: str, context: dict | None = None) -> dict:
        next_step = route_next_agent(prompt)
        llm_resp = gemini_llm.generate(
            prompt=f"User ({user_id}) request: '{prompt}'. Routing to sub-agent: {next_step}.",
            system_instruction="You are the GrowthOS Supervisor Agent."
        )
        return {
            "user_id": user_id,
            "next_step": next_step,
            "supervisor_summary": llm_resp,
            "context": context or {}
        }

supervisor_agent = SupervisorAgent()
