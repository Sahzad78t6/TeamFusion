from app.utils.helpers import generate_uuid

def fetch_curated_resources(target_role: str) -> list[dict]:
    return [
        {
            "id": generate_uuid(),
            "title": f"Mastering Advanced Systems for {target_role or 'AI Engineers'}",
            "type": "course",
            "provider": "GrowthOS Academy",
            "url": "https://coursera.org",
            "match_score": 0.96,
            "tags": ["AI", "Architecture", "Systems"]
        },
        {
            "id": generate_uuid(),
            "title": "LangGraph & Multi-Agent Design Patterns",
            "type": "article",
            "provider": "Medium / AI DeepDive",
            "url": "https://medium.com",
            "match_score": 0.92,
            "tags": ["Agents", "LangChain"]
        }
    ]
