"""Tools for the Learning Curator Agent."""
import os
from app.llm.provider import llm_provider

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompt.md")
SYSTEM = open(PROMPT_PATH).read() if os.path.exists(PROMPT_PATH) else ""

FALLBACK_RESOURCES = {
    "default": [
        {"title": "Foundations for {role} — Curated Course Path", "type": "course", "reason": "Covers the core fundamentals for {role}."},
        {"title": "The {role} Field Guide", "type": "book", "reason": "Broad, practical overview for someone targeting {role}."},
        {"title": "Building a Portfolio Project as a {role}", "type": "project", "reason": "Hands-on project to demonstrate {role} skills."},
        {"title": "{role} Career Roadmap — Community Article", "type": "article", "reason": "Real-world advice from working {role}s."},
    ]
}


async def curate_resources(target_role: str, tasks: list[dict]) -> list[dict]:
    """Curate resources via LLM or deterministic fallback."""
    task_titles = [t.get("title") for t in tasks]
    prompt = (
        f"Recommend 4-6 learning resources (JSON list under key 'resources', "
        f"each with title, type [video|book|course|article|project], reason) "
        f"for someone targeting '{target_role}' working on these tasks: {task_titles}."
    )
    
    result = llm_provider.generate_json(prompt, system_instruction=SYSTEM)
    if result and result.get("resources"):
        return result["resources"]

    return [
        {**r, "title": r["title"].format(role=target_role), "reason": r["reason"].format(role=target_role)}
        for r in FALLBACK_RESOURCES["default"]
    ]
