import logging
from app.utils.helpers import generate_uuid
from app.llm.groq_client import groq_llm
from app.agents.learning_curator.utils import CATEGORY_IMAGES
from app.exceptions import LLMJSONParseError, LLMUnavailableError

logger = logging.getLogger(__name__)

def generate_ai_recommendations(target_role: str = "AI Engineer", skills: list[str] | None = None, learning_style: str = "Interactive", raise_on_error: bool = False) -> list[dict]:
    user_skills = skills or ["Python", "FastAPI", "System Design"]
    skills_str = ", ".join(user_skills)

    prompt = (
        f"You are GrowthOS Learning Curator Agent. Generate 6 personalized, high-ROI learning resources for a developer whose target role is '{target_role}'. "
        f"Existing skills: '{skills_str}'. Preferred learning style: '{learning_style}'. "
        f"Provide 1 resource for each of these 6 media types: 'course', 'book', 'paper', 'video', 'article', 'podcast'. "
        f"Return ONLY a JSON array of 6 objects with fields: "
        f"'id' (string), 'title' (string), 'type' (string: 'course'/'book'/'paper'/'video'/'article'/'podcast'), "
        f"'provider' (string, e.g. 'GrowthOS Academy', 'Open Tech Publishing', 'ArXiv Research'), "
        f"'author' (string), 'duration' (string, e.g. '4h 30m', '6h 15m', '45m read'), "
        f"'url' (string), 'rating' (number 4.7-5.0), 'match_score' (number 0.88-0.99), 'progress_percentage' (number 0-100), 'tags' (list of 3 strings)."
    )

    result = groq_llm.generate_json(
        prompt=prompt,
        system_instruction="You are GrowthOS Learning Curator Agent. Return clean JSON array of 6 curated learning resources.",
        raise_on_error=raise_on_error
    )

    if isinstance(result, list) and len(result) >= 3 and isinstance(result[0], dict):
        for item in result:
            if "id" not in item or not item["id"]:
                item["id"] = generate_uuid()
            mtype = item.get("type", "course").lower()
            item["image_url"] = CATEGORY_IMAGES.get(mtype, CATEGORY_IMAGES["course"])
            if "author" not in item:
                item["author"] = item.get("provider", "GrowthOS AI")
            if "progress_percentage" not in item:
                item["progress_percentage"] = 25
            item["degraded"] = False
        return result

    if raise_on_error:
        raise LLMJSONParseError("Learning Curator Agent failed to parse valid JSON recommendations from Groq response.")

    reason = groq_llm.last_degraded_reason or "llm_unavailable"
    logger.error(f"Learning Curator LLM generation degraded (reason: {reason}).")
    role_title = target_role or "AI Startup Founder & Chief Architect"
    return [
        {
            "id": generate_uuid(),
            "title": f"Building Autonomous Multi-Agent Swarms for {role_title}",
            "type": "course",
            "provider": "GrowthOS Academy",
            "author": "GrowthOS AI Curators",
            "duration": "4h 30m",
            "rating": 4.9,
            "match_score": 0.98,
            "progress_percentage": 75,
            "url": "https://coursera.org",
            "image_url": CATEGORY_IMAGES["course"],
            "tags": ["Multi-Agent Workflows", "System Design", "Python"],
            "degraded": True,
            "reason": reason
        },
        {
            "id": generate_uuid(),
            "title": f"The Founder's Playbook: Zero to Series A in DeepTech & AI",
            "type": "book",
            "provider": "GrowthOS Open Tech Publishing",
            "author": "Industry Venture & Strategy Group",
            "duration": "6h 15m",
            "rating": 4.8,
            "match_score": 0.95,
            "progress_percentage": 40,
            "url": "https://amazon.com",
            "image_url": CATEGORY_IMAGES["book"],
            "tags": ["Startup", "Fundraising", "Strategy"],
            "degraded": True,
            "reason": reason
        },
        {
            "id": generate_uuid(),
            "title": "State of AI 2026: Reasoning Models, Multimodal Memory & Spatial Computing",
            "type": "paper",
            "provider": "ArXiv Open Research",
            "author": "AI Open Research Community",
            "duration": "45m read",
            "rating": 5.0,
            "match_score": 0.99,
            "progress_percentage": 100,
            "url": "https://arxiv.org",
            "image_url": CATEGORY_IMAGES["paper"],
            "tags": ["LLMs", "Multimodal", "Memory Retrieval"],
            "degraded": True,
            "reason": reason
        },
        {
            "id": generate_uuid(),
            "title": "Scaling Distributed Async Microservices with FastAPI & Vector DBs",
            "type": "video",
            "provider": "University Open Course",
            "author": "Engineering Education Team",
            "duration": "1h 45m",
            "rating": 4.9,
            "match_score": 0.93,
            "progress_percentage": 15,
            "url": "https://youtube.com",
            "image_url": CATEGORY_IMAGES["video"],
            "tags": ["FastAPI", "MongoDB", "Vector Search"],
            "degraded": True,
            "reason": reason
        },
        {
            "id": generate_uuid(),
            "title": "Designing Resilient Self-Healing AI Workflows in Production",
            "type": "article",
            "provider": "AI Engineering Review",
            "author": "Production MLOps Reviewers",
            "duration": "20m read",
            "rating": 4.8,
            "match_score": 0.91,
            "progress_percentage": 60,
            "url": "https://medium.com",
            "image_url": CATEGORY_IMAGES["article"],
            "tags": ["MLOps", "Reliability", "Agentic Frameworks"],
            "degraded": True,
            "reason": reason
        },
        {
            "id": generate_uuid(),
            "title": "Architecting Cognitive AI Systems & Human-AI Collaboration",
            "type": "podcast",
            "provider": "Tech Vision Series",
            "author": "Tech Vision Podcast Host",
            "duration": "2h 10m",
            "rating": 4.9,
            "match_score": 0.96,
            "progress_percentage": 0,
            "url": "https://spotify.com",
            "image_url": CATEGORY_IMAGES["podcast"],
            "tags": ["AI Future", "Cognition", "Neuroscience"],
            "degraded": True,
            "reason": reason
        }
    ]
