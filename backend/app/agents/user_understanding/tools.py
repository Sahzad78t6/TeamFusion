import logging
from app.llm.groq_client import groq_llm
from app.exceptions import LLMJSONParseError, LLMUnavailableError

logger = logging.getLogger(__name__)

def generate_identity_twin_analysis(onboarding_data: dict, raise_on_error: bool = False) -> dict:
    goal = onboarding_data.get("goal") or onboarding_data.get("target_role") or "AI Architect"
    skills = onboarding_data.get("skills", ["Python", "FastAPI"])
    interests = onboarding_data.get("interests", ["AI", "Machine Learning"])
    experience = onboarding_data.get("experience", "Intermediate")
    learning_style = onboarding_data.get("learning_style", "Hands-on projects")

    prompt = (
        f"Analyze user onboarding dataset for career goal: '{goal}'. "
        f"Skills: {skills}. Interests: {interests}. Experience: {experience}. Learning style: {learning_style}. "
        f"Provide structured JSON output with keys: "
        f"'identity_score' (number 70-98), 'identity_drift_percentage' (number 5-25), "
        f"'key_strengths' (list of strings), 'skill_gaps' (list of strings), 'strategic_insight' (string)."
    )

    result = groq_llm.generate_json(
        prompt=prompt,
        system_instruction="You are GrowthOS User Understanding Agent. Analyze developer identity and return clean JSON.",
        raise_on_error=raise_on_error
    )

    if isinstance(result, dict) and "identity_score" in result:
        result["degraded"] = False
        return result

    if raise_on_error:
        raise LLMJSONParseError("User Understanding Agent failed to parse valid JSON from Groq response.")

    reason = groq_llm.last_degraded_reason or "llm_unavailable"
    logger.error(f"User Understanding LLM generation degraded (reason: {reason}).")
    return {
        "identity_score": 88.5,
        "identity_drift_percentage": 11.4,
        "key_strengths": skills + [s for s in interests if s not in skills],
        "skill_gaps": ["System Architecture", "Vector Caching", "Model Training"],
        "strategic_insight": f"Strong alignment for {goal}. Recommend focusing on core architecture.",
        "degraded": True,
        "reason": reason
    }
