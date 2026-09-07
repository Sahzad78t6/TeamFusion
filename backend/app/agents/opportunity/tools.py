"""Tools for the Opportunity Agent."""
import os
import random
import logging
from app.llm.provider import llm_provider

logger = logging.getLogger(__name__)

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompt.md")
SYSTEM = open(PROMPT_PATH).read() if os.path.exists(PROMPT_PATH) else ""

# Static dataset for MVP matching
STATIC_OPPORTUNITIES = [
    {"id": "opp_001", "type": "hackathon", "title": "AI Innovation Hackathon", "skills_required": ["Python", "Machine Learning", "AI"]},
    {"id": "opp_002", "type": "internship", "title": "Software Engineering Intern", "skills_required": ["Python", "React", "TypeScript"]},
    {"id": "opp_003", "type": "open-source", "title": "Contribute to LangChain", "skills_required": ["Python", "LLMs"]},
    {"id": "opp_004", "type": "event", "title": "Tech Leadership Summit", "skills_required": ["Leadership", "System Design"]},
]


async def match_opportunities(identity: dict) -> list[dict]:
    """Match opportunities using LLM filtering or deterministic fallback."""
    target_role = identity.get("target_role", "Software Engineer")
    skills = identity.get("skills", ["Python"])

    prompt = (
        f"Filter and rank these opportunities for a candidate targeting '{target_role}' "
        f"with skills {skills}. Return JSON list under key 'opportunities', each with "
        f"'id', 'title', 'type', and 'match_reason'.\n\nOpportunities: {STATIC_OPPORTUNITIES}"
    )

    result = llm_provider.generate_json(prompt, system_instruction=SYSTEM)
    if result and result.get("opportunities"):
        return [
            {**opp, "ai_generated": True, "match_source": "llm"}
            for opp in result["opportunities"]
        ]

    # FALLBACK TRIGGER — LLM unavailable, using keyword intersection over static dataset.
    logger.error(
        f"FALLBACK TRIGGER: Opportunity agent falling back to deterministic keyword matching. "
        f"target_role='{target_role}', skills={skills}. LLM is unavailable. "
        f"Set OPENAI_API_KEY to enable real AI opportunity matching."
    )

    # Deterministic fallback: simple keyword intersection
    user_skills_lower = {s.lower() for s in skills}
    matched = []
    for opp in STATIC_OPPORTUNITIES:
        req_skills_lower = {s.lower() for s in opp["skills_required"]}
        if user_skills_lower.intersection(req_skills_lower):
            matched.append({
                "id": opp["id"],
                "title": opp["title"],
                "type": opp["type"],
                "match_reason": f"Matches your skills in {', '.join(user_skills_lower.intersection(req_skills_lower))}.",
                # Visibility: allows frontend/devtools to verify AI vs fallback
                "ai_generated": False,
                "match_source": "deterministic_keyword_fallback",
            })

    if not matched:
        # Fallback to random if no exact match (MVP behavior)
        sampled = random.sample(STATIC_OPPORTUNITIES, min(2, len(STATIC_OPPORTUNITIES)))
        return [
            {
                **s,
                "match_reason": f"Good general opportunity for {target_role}.",
                "ai_generated": False,
                "match_source": "random_fallback",
            }
            for s in sampled
        ]

    return matched
