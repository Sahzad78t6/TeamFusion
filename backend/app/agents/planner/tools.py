import logging
from app.utils.helpers import generate_uuid
from app.llm.gemini import gemini_llm

logger = logging.getLogger(__name__)

def generate_ai_roadmap(goals: list[str], target_role: str = "AI Architect", skills: list[str] | None = None) -> dict:
    skills_str = ", ".join(skills or ["Python", "FastAPI", "AI"])
    goals_str = ", ".join(goals) if goals else f"Mastering {target_role}"

    prompt = (
        f"Generate a structured daily learning roadmap for target role: '{target_role}'. "
        f"User goals: '{goals_str}'. Current skills: '{skills_str}'. "
        f"Return JSON object with keys: "
        f"'ai_feedback' (string providing summary advice), "
        f"'tasks' (list of objects with fields: 'id' (string), 'title' (string), 'category' (string), 'duration_mins' (integer), 'priority' (string: 'high'/'medium'/'low'), 'completed' (boolean))."
    )

    result = gemini_llm.generate_json(
        prompt=prompt,
        system_instruction="You are GrowthOS Planner Agent. Generate structured daily learning roadmaps."
    )

    if isinstance(result, dict) and "tasks" in result and isinstance(result["tasks"], list):
        for task in result["tasks"]:
            if "id" not in task or not task["id"]:
                task["id"] = generate_uuid()
            if "completed" not in task:
                task["completed"] = False
        return result

    # Structured fallback tasks if Gemini API key or JSON format fails
    fallback_tasks = [
        {
            "id": generate_uuid(),
            "title": f"Implement LangGraph Multi-Agent Workflows for {target_role}",
            "category": "Agentic Architecture",
            "duration_mins": 60,
            "priority": "high",
            "completed": False
        },
        {
            "id": generate_uuid(),
            "title": "Configure Mem0 Vector Memory Caching & Retrieval",
            "category": "Memory Systems",
            "duration_mins": 45,
            "priority": "high",
            "completed": False
        },
        {
            "id": generate_uuid(),
            "title": "Optimize FastAPI Async Controllers & Database Repositories",
            "category": "Backend Engineering",
            "duration_mins": 45,
            "priority": "medium",
            "completed": False
        },
        {
            "id": generate_uuid(),
            "title": "Review Daily Cognitive Sentiment & Reflection Analytics",
            "category": "Self-Reflection",
            "duration_mins": 15,
            "priority": "low",
            "completed": False
        }
    ]

    return {
        "ai_feedback": f"Roadmap generated for {target_role}. Focus on high-priority agentic architecture modules first.",
        "tasks": fallback_tasks
    }
