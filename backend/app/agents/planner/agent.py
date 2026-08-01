from app.agents.planner.tools import generate_daily_tasks
from app.llm.gemini import gemini_llm

class PlannerAgent:
    def create_plan(self, user_id: str, goals: list[str]) -> dict:
        tasks = generate_daily_tasks(goals)
        feedback = gemini_llm.generate(
            prompt=f"Created {len(tasks)} tasks for goals: {goals}.",
            system_instruction="Provide feedback on productivity schedule."
        )
        return {
            "user_id": user_id,
            "goals": goals,
            "tasks": tasks,
            "ai_feedback": feedback
        }

planner_agent = PlannerAgent()
