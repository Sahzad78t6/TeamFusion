import os
import csv
import logging
from app.utils.helpers import generate_uuid
from app.exceptions import GrowthOSError

logger = logging.getLogger(__name__)

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../ml/datasets/opportunities.csv"))

def find_matched_opportunities(role: str = "", user_skills: list[str] | None = None, goal: str = "", experience: str = "", raise_on_error: bool = False) -> list[dict]:
    user_skills_set = {s.lower().strip() for s in (user_skills or ["python", "ai", "fastapi"])}
    query = (role + " " + goal).lower()
    results = []

    if not os.path.exists(CSV_PATH):
        logger.error(f"Opportunities dataset missing at {CSV_PATH}")
        if raise_on_error:
            raise FileNotFoundError(f"Opportunities dataset missing at {CSV_PATH}")

    if os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    opp_skills = [s.lower().strip() for s in row.get("skills_required", "").split(",")]
                    matched = sum(1 for s in opp_skills if any(u in s or s in u for u in user_skills_set))
                    total = max(len(opp_skills), 1)
                    skill_score = matched / total

                    title_desc = (row.get("title", "") + " " + row.get("description", "")).lower()
                    query_score = 0.2 if any(w in title_desc for w in query.split() if len(w) > 2) else 0.0

                    base_score = float(row.get("min_relevance_score", 0.85))
                    final_score = round(min(0.99, max(0.70, base_score * 0.7 + skill_score * 0.2 + query_score)), 2)

                    results.append({
                        "id": row.get("id") or generate_uuid(),
                        "title": row.get("title", "AI Opportunity"),
                        "company": row.get("company", "GrowthOS Partner"),
                        "location": row.get("location", "Remote"),
                        "type": row.get("type", "job"),
                        "relevance_score": final_score,
                        "description": row.get("description", ""),
                        "url": row.get("url", "https://growthos.ai")
                    })
        except Exception as e:
            logger.error(f"Failed to parse opportunities.csv ({e}).")
            if raise_on_error:
                raise GrowthOSError(f"Failed to parse opportunities dataset: {e}")

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results
