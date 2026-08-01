from app.agents.reflection.tools import compute_burnout_risk_indicator
from app.llm.gemini import gemini_llm

class ReflectionAgent:
    def process(self, user_id: str, mood_score: int, energy_level: int, notes: str) -> dict:
        risk = compute_burnout_risk_indicator(mood_score, energy_level)
        insight = gemini_llm.generate(
            prompt=f"Mood: {mood_score}/5, Energy: {energy_level}/5. Notes: '{notes}'. Risk level: {risk}.",
            system_instruction="Provide compassionate burnout prevention reflection advice."
        )
        return {
            "user_id": user_id,
            "risk_level": risk,
            "ai_insight": insight
        }

reflection_agent = ReflectionAgent()
