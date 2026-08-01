"""Tools for the User Understanding Agent."""
from app.llm.provider import llm_provider
from app.utils.text_normalize import normalize_role_string, normalize_skills
from app.llm.client import complete_json
import os

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompt.md")
SYSTEM = open(PROMPT_PATH).read() if os.path.exists(PROMPT_PATH) else ""


async def extract_profile_fields(onboarding: dict) -> dict:
    """
    Extract and normalize profile fields from onboarding data.
    Tries LLM extraction first, falls back to deterministic normalization.
    """
    chat_messages = onboarding.get("chat_messages") or []
    if chat_messages:
        prompt = (
            "Extract a JSON object with keys: target_role, skills (list), "
            "interests (list), learning_style, available_time_per_week_hours "
            "(int), aspirations (string) from this onboarding data and chat "
            f"history. Correct any obvious typos.\n\nOnboarding: {onboarding}"
        )
        result = await complete_json(prompt, system=SYSTEM)
        if result:
            result["target_role"] = normalize_role_string(
                result.get("target_role", "") or onboarding.get("target_role", "AI Engineer")
            )
            result["skills"] = normalize_skills(result.get("skills") or onboarding.get("skills", []))
            return result

    # Deterministic fallback — no LLM needed
    raw_role = onboarding.get("target_role") or onboarding.get("goal") or "AI Engineer"
    return {
        "target_role": normalize_role_string(raw_role),
        "skills": normalize_skills(onboarding.get("skills", [])) or ["Python"],
        "interests": onboarding.get("interests", []),
        "learning_style": onboarding.get("learning_style") or "hands-on",
        "available_time_per_week_hours": onboarding.get("available_time_per_week_hours") or 5,
        "aspirations": onboarding.get("aspirations") or "",
    }
