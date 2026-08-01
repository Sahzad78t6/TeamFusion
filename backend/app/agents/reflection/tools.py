"""Tools for the Reflection Agent."""
import os
from app.llm.provider import llm_provider

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompt.md")
SYSTEM = open(PROMPT_PATH).read() if os.path.exists(PROMPT_PATH) else ""


async def generate_reflection_insights(data: dict) -> str:
    """Generate empathetic insights based on daily reflection."""
    prompt = (
        f"Generate a short, empathetic AI insight (2-3 sentences max) for a user's daily reflection.\n"
        f"Data: Mood={data.get('mood_score')}/5, Energy={data.get('energy_level')}/5, "
        f"Completed Tasks={len(data.get('completed_tasks', []))}, "
        f"Wins='{data.get('wins', '')}', Challenges='{data.get('challenges', '')}', "
        f"Reflection='{data.get('reflection', '')}'.\n"
        f"Return ONLY the insight text string."
    )
    
    result = llm_provider.generate(prompt, system_instruction=SYSTEM)
    if result:
        return result

    # Deterministic fallback
    mood = data.get("mood_score", 4)
    if mood >= 4:
        return "Great job today! You're making solid progress. Keep up the momentum!"
    elif mood <= 2:
        return "It sounds like today was tough. Remember to take breaks and rest. Progress isn't always linear."
    return "Good effort today. Reflect on what worked well and adjust your approach for tomorrow."
