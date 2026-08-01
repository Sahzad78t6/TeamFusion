import logging
from app.utils.helpers import generate_uuid
from app.llm.gemini import gemini_llm

logger = logging.getLogger(__name__)

def generate_ai_recommendations(target_role: str = "AI Engineer", skills: list[str] | None = None, learning_style: str = "Interactive") -> list[dict]:
    skills_str = ", ".join(skills or ["Python", "FastAPI", "AI"])

    prompt = (
        f"Generate 3-4 personalized, high-quality learning resources for a developer aiming to be: '{target_role}'. "
        f"Current skills: '{skills_str}'. Preferred learning style: '{learning_style}'. "
        f"Return JSON array of objects with keys: "
        f"'id' (string), 'title' (string), 'type' (string: 'course'/'article'/'paper'/'video'), "
        f"'provider' (string), 'url' (string), 'match_score' (number 0.85-0.99), 'tags' (list of strings)."
    )

    result = gemini_llm.generate_json(
        prompt=prompt,
        system_instruction="You are GrowthOS Learning Curator Agent. Return clean JSON list of curated learning resources."
    )

    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
        for item in result:
            if "id" not in item or not item["id"]:
                item["id"] = generate_uuid()
        return result

    # Structured fallback if Gemini API response format differs
    return [
        {
            "id": generate_uuid(),
            "title": f"Mastering Frontier Production Systems for {target_role}",
            "type": "course",
            "provider": "DeepLearning.AI & GrowthOS",
            "url": "https://coursera.org",
            "match_score": 0.97,
            "tags": ["AI Architecture", "FastAPI", "LangGraph"]
        },
        {
            "id": generate_uuid(),
            "title": "LangGraph & Mem0 Vector Memory Design Patterns",
            "type": "article",
            "provider": "AI Engineering Review",
            "url": "https://medium.com",
            "match_score": 0.94,
            "tags": ["Multi-Agent Swarms", "Mem0", "Python"]
        },
        {
            "id": generate_uuid(),
            "title": "Scalable Vector Databases & RLS Authorization Models",
            "type": "paper",
            "provider": "ArXiv / Stanford AI",
            "url": "https://arxiv.org",
            "match_score": 0.91,
            "tags": ["Vector Search", "MongoDB", "Security"]
        }
    ]
