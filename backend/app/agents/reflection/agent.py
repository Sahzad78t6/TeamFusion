import logging
from app.agents.reflection.schemas import ReflectionInput
from app.agents.reflection.tools import compute_burnout_risk_indicator
from app.llm.groq_client import groq_llm
from app.database.repositories.reflection_repository import reflection_repository
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.analytics_repository import analytics_repository
from app.memory.memory_manager import memory_manager
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)

def extract_sentiment_scores(notes: str, raise_on_error: bool = False) -> tuple[int, int]:
    if not notes:
        return (3, 3)

    prompt = (
        f"Analyze the following user reflection note: '{notes}'. "
        f"Estimate their mood_score (1 to 5, where 1 is miserable/burnt out, 5 is joyful/excited) "
        f"and energy_level (1 to 5, where 1 is exhausted, 5 is fully energized). "
        f"Return ONLY valid JSON in the format: {{\"mood_score\": int, \"energy_level\": int}}"
    )
    result = groq_llm.generate_json(
        prompt=prompt,
        system_instruction="You are a sentiment analyzer. Return valid JSON containing mood_score and energy_level numbers from 1 to 5.",
        raise_on_error=raise_on_error
    )
    if isinstance(result, dict) and "mood_score" in result and "energy_level" in result:
        try:
            m = max(1, min(5, int(result["mood_score"])))
            e = max(1, min(5, int(result["energy_level"])))
            return (m, e)
        except Exception:
            pass

    lower_notes = notes.lower()
    negative_keywords = ["stress", "burnt out", "burnout", "exhaust", "overwhelmed", "tired", "anxious", "depressed", "struggling", "hate", "give up", "hard", "miserable", "drained", "awful", "bad", "quit"]
    positive_keywords = ["excited", "great", "awesome", "productive", "happy", "loving it", "energized", "fantastic", "good", "amazing"]

    neg_count = sum(1 for kw in negative_keywords if kw in lower_notes)
    pos_count = sum(1 for kw in positive_keywords if kw in lower_notes)

    if neg_count > pos_count:
        m_score = max(1, 4 - (neg_count * 2))
        e_score = max(1, 4 - (neg_count * 2))
        return (m_score, e_score)
    elif pos_count > neg_count:
        return (4, 4)

    return (3, 3)

class ReflectionAgent:
    async def process_and_save(self, user_id: str, data: dict, raise_on_error: bool = False) -> dict:
        logger.info(f"ReflectionAgent processing daily reflection for user {user_id}")

        # Pydantic validation before calling Groq or Mongo
        validated_input = ReflectionInput(**data)
        val_dict = validated_input.model_dump()

        notes = val_dict.get("reflection") or val_dict.get("notes") or ""
        has_explicit_mood = val_dict.get("mood") is not None or val_dict.get("mood_score") is not None
        has_explicit_energy = val_dict.get("motivation") is not None or val_dict.get("energy_level") is not None

        if not has_explicit_mood or not has_explicit_energy:
            extracted_mood, extracted_energy = extract_sentiment_scores(notes, raise_on_error=raise_on_error)
            mood_score = val_dict.get("mood") or val_dict.get("mood_score") or extracted_mood
            energy_level = val_dict.get("motivation") or val_dict.get("energy_level") or extracted_energy
        else:
            mood_score = val_dict.get("mood") or val_dict.get("mood_score") or 3
            energy_level = val_dict.get("motivation") or val_dict.get("energy_level") or 3

        study_hours = float(val_dict.get("study_hours") or 2.5)
        completed_tasks = val_dict.get("completed_tasks") or []
        skipped_tasks = val_dict.get("skipped_tasks") or []
        timestamp = get_utc_now()

        risk = compute_burnout_risk_indicator(mood_score, energy_level, study_hours)

        prompt = (
            f"Daily Reflection Notes: '{notes}'. Mood score: {mood_score}/5. Motivation: {energy_level}/5. "
            f"Study hours logged: {study_hours}h. Completed tasks count: {len(completed_tasks)}. Skipped tasks: {len(skipped_tasks)}. "
            f"Calculated burnout risk level: {risk}. "
            f"Provide 2-3 sentences of empathetic, actionable productivity advice."
        )

        ai_insight = groq_llm.generate(
            prompt=prompt,
            system_instruction="You are GrowthOS Reflection Agent. Provide encouraging, supportive productivity and burnout coaching.",
            raise_on_error=raise_on_error
        )

        degraded = getattr(groq_llm, "last_degraded", False)
        reason = getattr(groq_llm, "last_degraded_reason", None)

        reflection_doc = {
            "user_id": user_id,
            "reflection": notes,
            "notes": notes,
            "mood": mood_score,
            "mood_score": mood_score,
            "motivation": energy_level,
            "energy_level": energy_level,
            "study_hours": study_hours,
            "completed_tasks": completed_tasks,
            "skipped_tasks": skipped_tasks,
            "timestamp": timestamp,
            "risk_level": risk,
            "ai_insight": ai_insight,
            "degraded": degraded,
        }
        if degraded and reason:
            reflection_doc["reason"] = reason

        saved_reflection = await reflection_repository.create_reflection(user_id, reflection_doc)

        await analytics_repository.update_analytics(
            user_id=user_id,
            add_hours=study_hours,
            completed_count=len(completed_tasks),
            risk_level=risk.lower()
        )

        await identity_repository.update_identity(user_id, {
            "last_reflection_at": timestamp,
            "burnout_risk_level": risk
        })

        # Mem0 call wrapped safely
        memory_manager.save_user_fact(
            user_id,
            f"Log reflection note (risk: {risk}): '{notes[:60]}'."
        )

        return saved_reflection

reflection_agent = ReflectionAgent()
