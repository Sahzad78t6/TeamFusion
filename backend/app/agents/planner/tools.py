"""Tools for the Planner Agent."""
import uuid
import os
import logging
from app.llm.provider import llm_provider

logger = logging.getLogger(__name__)

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompt.md")
SYSTEM = open(PROMPT_PATH).read() if os.path.exists(PROMPT_PATH) else ""

FALLBACK_TEMPLATE_TASKS = [
    ("Study Core Fundamentals of {role}", "Spend focused time on the foundational concepts for {role}.", "high"),
    ("Build a Real-World Project for {role}", "Apply what you're learning in a small hands-on project.", "high"),
    ("Network with Professionals in {role}", "Reach out to 2-3 people working as {role} for informational chats.", "medium"),
    ("Review Progress and Adjust Plan", "Reflect on the week and update priorities.", "low"),
]


async def generate_ai_roadmap(goals: list[str], target_role: str, skills: list[str]) -> dict:
    """Generate roadmap tasks via LLM or fallback."""
    prompt = (
        f"Create a roadmap as JSON with keys 'tasks' (list of objects with "
        f"title, description, priority) and 'ai_feedback' (string) for someone "
        f"with goals {goals}, targeting the role '{target_role}', with current "
        f"skills {skills}. 4-6 tasks, balanced and prioritized."
    )

    result = llm_provider.generate_json(prompt, system_instruction=SYSTEM)

    if result and result.get("tasks"):
        for t in result["tasks"]:
            t["id"] = str(uuid.uuid4())[:8]
            t.setdefault("done", False)
        # Mark as AI-generated so callers can surface this in responses
        result["ai_generated"] = True
        result["generation_source"] = "llm"
        return result

    # FALLBACK TRIGGER — LLM unavailable or returned no tasks.
    # This produces a hardcoded template roadmap, NOT a personalized AI plan.
    logger.error(
        f"FALLBACK TRIGGER: Planner agent falling back to FALLBACK_TEMPLATE_TASKS for role='{target_role}'. "
        f"LLM is unavailable or returned no tasks. Set OPENAI_API_KEY to enable real AI roadmap generation."
    )

    tasks = [
        {
            "id": str(uuid.uuid4())[:8],
            "title": title.format(role=target_role),
            "description": desc.format(role=target_role),
            "priority": priority,
            "done": False,
        }
        for title, desc, priority in FALLBACK_TEMPLATE_TASKS
    ]
    return {
        "tasks": tasks,
        "ai_feedback": f"Roadmap generated for {target_role}. Focus on the high-priority tasks first.",
        # Visibility fields — inspectable via browser devtools / API response
        "ai_generated": False,
        "generation_source": "deterministic_fallback",
    }
