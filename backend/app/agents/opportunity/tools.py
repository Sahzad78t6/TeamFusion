from app.utils.helpers import generate_uuid

def find_matched_opportunities(role: str) -> list[dict]:
    return [
        {
            "id": generate_uuid(),
            "title": f"Senior {role or 'AI Developer'} - Remote",
            "company": "DeepGrowth Tech",
            "location": "San Francisco, CA (Remote)",
            "type": "job",
            "relevance_score": 0.94,
            "description": "Leading development of agentic AI systems.",
            "url": "https://linkedin.com"
        },
        {
            "id": generate_uuid(),
            "title": "Global AI Hackathon 2026",
            "company": "OpenAI / Anthropic Partner Series",
            "location": "Global / Online",
            "type": "hackathon",
            "relevance_score": 0.98,
            "description": "$50k prize pool for multi-agent LLM systems.",
            "url": "https://devpost.com"
        }
    ]
