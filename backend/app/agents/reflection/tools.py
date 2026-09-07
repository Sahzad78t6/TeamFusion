"""Tools for the Reflection Agent."""
import os
import logging
from app.llm.provider import llm_provider

logger = logging.getLogger(__name__)

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompt.md")
SYSTEM = open(PROMPT_PATH).read() if os.path.exists(PROMPT_PATH) else ""


async def generate_reflection_insights(data: dict) -> tuple[str, bool]:
    """
    Generate empathetic insights based on daily reflection.

    Returns:
        (insight_text, ai_generated) — callers should store ai_generated
        in the reflection document for visibility in API responses.
    """
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
        return result, True

    # FALLBACK TRIGGER — LLM unavailable, returning hardcoded mood-based string.
    logger.error(
        f"FALLBACK TRIGGER: Reflection agent falling back to hardcoded mood string. "
        f"mood_score={data.get('mood_score')}, LLM is unavailable. "
        f"Set OPENAI_API_KEY to enable real AI reflection insights."
    )

    # Deterministic fallback
    mood = data.get("mood_score", 4)
    if mood >= 4:
        text = "Great job today! You're making solid progress. Keep up the momentum!"
    elif mood <= 2:
        text = "It sounds like today was tough. Remember to take breaks and rest. Progress isn't always linear."
    else:
        text = "Good effort today. Reflect on what worked well and adjust your approach for tomorrow."

    return text, False


def compute_burnout_risk_indicator(mood: int, energy: int, study_hours: float = 0.0) -> str:
    """Helper to compute burnout risk level based on mood, energy, and hours."""
    if mood <= 2 or energy <= 2 or study_hours >= 10.0:
        return "HIGH_RISK"
    elif mood == 3 or energy == 3 or study_hours >= 6.0:
        return "MODERATE"
    return "LOW"
