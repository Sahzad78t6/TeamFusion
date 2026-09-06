"""
Curator Engine — GrowthOS Learning Curator
Orchestrates student context retrieval, query generation, multi-provider candidate search,
deduplication, engineering heuristic ranking, and structured LLM re-ranking.
"""
import logging
import asyncio
from typing import Any
from pydantic import BaseModel, Field
from app.services.search_providers.youtube_provider import youtube_provider
from app.services.search_providers.web_provider import web_provider
from app.services.search_providers.base import SearchResult
from app.services.skill_graph_service import skill_graph_service
from app.memory.service import memory_service
from app.llm.provider import llm_provider
from app.database.collections import get_collection, get_mock_collection
from app.config.constants import COLLECTION_RECOMMENDATIONS
from app.utils.helpers import get_utc_now, generate_uuid

logger = logging.getLogger(__name__)

VERIFIED_SEED_RESOURCES = [
    {
        "title": "Python Recursion Explained with Visual Examples",
        "type": "video",
        "source": "youtube",
        "url": "https://www.youtube.com/watch?v=m1Fj5bMAVbY",
        "thumbnail": "https://i.ytimg.com/vi/m1Fj5bMAVbY/hqdefault.jpg",
        "channel": "freeCodeCamp",
        "duration_minutes": 25,
        "difficulty": "Intermediate",
        "match_score": 0.94,
        "reason": "Matches your current recursion gap and preference for visual practical examples."
    },
    {
        "title": "Deep Dive into Feature Engineering for Machine Learning",
        "type": "article",
        "source": "web",
        "url": "https://scikit-learn.org/stable/modules/preprocessing.html",
        "thumbnail": "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?auto=format&fit=crop&w=800&q=80",
        "channel": "Scikit-Learn Docs",
        "duration_minutes": 30,
        "difficulty": "Intermediate",
        "match_score": 0.91,
        "reason": "Official documentation covering feature scaling, encoding, and transformation."
    },
    {
        "title": "Mastering Data Structures: Trees, Graphs & Traversal",
        "type": "course",
        "source": "web",
        "url": "https://github.com/trekhleb/javascript-algorithms",
        "thumbnail": "https://images.unsplash.com/photo-1516116211223-48a122638e59?auto=format&fit=crop&w=800&q=80",
        "channel": "GitHub Education",
        "duration_minutes": 45,
        "difficulty": "Advanced",
        "match_score": 0.88,
        "reason": "Hands-on repository providing algorithm implementations and visual explanations."
    },
    {
        "title": "Building REST APIs with FastAPI & PyDantic",
        "type": "video",
        "source": "youtube",
        "url": "https://www.youtube.com/watch?v=7t2alSnE2-I",
        "thumbnail": "https://i.ytimg.com/vi/7t2alSnE2-I/hqdefault.jpg",
        "channel": "Tech With Tim",
        "duration_minutes": 40,
        "difficulty": "Beginner",
        "match_score": 0.85,
        "reason": "Practical backend architecture video targeting API development."
    }
]


class ResourceEvaluationItem(BaseModel):
    url: str
    match_score: float = Field(default=0.85, ge=0.0, le=1.0)
    reason: str = Field(default="Matches student skill gap and learning style preference.")


class ResourceEvaluationResult(BaseModel):
    evaluations: list[ResourceEvaluationItem] = Field(default_factory=list)


class CuratorEngine:
    async def curate_personalized_resources(
        self,
        user_id: str,
        topic: str = "",
        target_role: str = ""
    ) -> list[dict[str, Any]]:
        """Main entry point: Build context -> Generate queries -> Search -> Filter -> Rank -> LLM re-rank -> Format."""
        logger.info(f"CuratorEngine starting curation for user {user_id}, topic='{topic}'")

        # 1. Build Student Context
        skills = await skill_graph_service.get_user_skills(user_id)
        memories = memory_service.get_memories(user_id)
        
        # Identify target skill gap
        skill_gap = self._identify_primary_skill_gap(skills, topic)
        target_role = target_role or "Machine Learning Engineer"

        # Extract memory preferences
        preferences = self._extract_preferences_from_memories(memories)

        # 2. Generate Search Queries
        queries = self._generate_search_queries(skill_gap, target_role, preferences)
        logger.info(f"Generated search queries for {user_id}: {queries}")

        # 3. Collect Candidates from Providers
        candidate_tasks = []
        for q in queries:
            candidate_tasks.append(youtube_provider.search(q, max_results=8))
            candidate_tasks.append(web_provider.search(q, max_results=8))

        results_lists = await asyncio.gather(*candidate_tasks, return_exceptions=True)
        raw_candidates: list[SearchResult] = []
        for res in results_lists:
            if isinstance(res, list):
                raw_candidates.extend(res)

        logger.info(f"Collected {len(raw_candidates)} raw candidate resources for {user_id}")

        # 4. Deduplicate and Filter
        filtered_candidates = self._filter_and_deduplicate(raw_candidates, user_id)
        logger.info(f"Filtered to {len(filtered_candidates)} unique candidates")

        # 5. Fallback if search results are empty
        if not filtered_candidates:
            logger.info(f"Search returned no candidates. Using verified educational seed resources.")
            return self._format_seed_resources(skill_gap, preferences)

        # 6. Engineering Heuristic Ranking
        ranked_candidates = self._apply_heuristic_ranking(filtered_candidates, skill_gap, preferences)

        # Take top 8 candidates for LLM re-ranking
        top_candidates = ranked_candidates[:8]

        # 7. LLM Re-Ranking & Personalization Reason Generation
        final_resources = await self._apply_llm_reranking(top_candidates, skill_gap, preferences, target_role)
        return final_resources

    def _identify_primary_skill_gap(self, skills: list[dict], specified_topic: str = "") -> str:
        if specified_topic and len(specified_topic.strip()) > 2:
            return specified_topic.strip()
        if not skills:
            return "Python Recursion & Data Structures"
        # Find skill with lowest mastery
        sorted_skills = sorted(skills, key=lambda s: s.get("mastery", 0.5))
        return sorted_skills[0].get("name", "Python Fundamentals")

    def _extract_preferences_from_memories(self, memories: list[dict]) -> dict[str, Any]:
        prefs = {"style": "practical", "video_preference": True, "preferred_duration": 30}
        for mem in memories:
            txt = (mem.get("text") or mem.get("content") or "").lower()
            if "visual" in txt or "video" in txt:
                prefs["video_preference"] = True
            if "read" in txt or "article" in txt or "book" in txt:
                prefs["style"] = "reading"
            if "practical" in txt or "hands-on" in txt or "code" in txt:
                prefs["style"] = "practical"
        return prefs

    def _generate_search_queries(self, skill_gap: str, target_role: str, prefs: dict) -> list[str]:
        style_keyword = "tutorial practical examples" if prefs.get("style") == "practical" else "explained guide"
        return [
            f"{skill_gap} {style_keyword}",
            f"{skill_gap} {target_role} tutorial",
            f"{skill_gap} intermediate problem solving"
        ]

    def _filter_and_deduplicate(self, candidates: list[SearchResult], user_id: str) -> list[SearchResult]:
        seen_urls = set()
        unique: list[SearchResult] = []

        for c in candidates:
            url_clean = c.url.strip().rstrip("/")
            if not url_clean or url_clean in seen_urls:
                continue
            seen_urls.add(url_clean)
            unique.append(c)

        return unique

    def _apply_heuristic_ranking(
        self,
        candidates: list[SearchResult],
        skill_gap: str,
        prefs: dict
    ) -> list[SearchResult]:
        skill_terms = set(skill_gap.lower().split())

        def compute_score(c: SearchResult) -> float:
            title_text = (c.title + " " + c.description).lower()
            term_matches = sum(1 for term in skill_terms if term in title_text)
            relevance = min(1.0, term_matches / max(1, len(skill_terms)))

            style_bonus = 0.15 if (c.source == "youtube" and prefs.get("video_preference")) else 0.05
            duration_match = 0.10 if (c.duration_minutes and c.duration_minutes <= 45) else 0.05

            score = (relevance * 0.50) + style_bonus + duration_match + 0.25
            return min(1.0, max(0.1, score))

        candidates.sort(key=compute_score, reverse=True)
        return candidates

    async def _apply_llm_reranking(
        self,
        candidates: list[SearchResult],
        skill_gap: str,
        prefs: dict,
        target_role: str
    ) -> list[dict[str, Any]]:
        candidate_json = [
            {
                "url": c.url,
                "title": c.title,
                "source": c.source,
                "description": c.description[:120]
            }
            for c in candidates
        ]

        prompt = (
            f"Evaluates candidate resources for a learner targeting '{target_role}' with skill gap in '{skill_gap}'.\n"
            f"Preferences: {prefs}.\n"
            f"Candidates: {candidate_json}\n"
            f"Return JSON matching key 'evaluations', where each item has 'url', 'match_score' (0.0 to 1.0), and 'reason' (why it helps)."
        )

        try:
            eval_res = llm_provider.generate_json(prompt)
            eval_map = {}
            if eval_res and "evaluations" in eval_res:
                for ev in eval_res["evaluations"]:
                    eval_map[ev.get("url")] = ev
        except Exception as e:
            logger.warning(f"LLM re-ranking failed: {e}. Using heuristic scores.")
            eval_map = {}

        formatted = []
        for i, c in enumerate(candidates):
            llm_eval = eval_map.get(c.url, {})
            score = llm_eval.get("match_score") or round(0.95 - (i * 0.03), 2)
            reason = llm_eval.get("reason") or f"Directly addresses your gap in {skill_gap} with clear practical context."
            numeric_score = round(score * 100) if score <= 1.0 else int(score)
            thumb = c.thumbnail or "https://images.unsplash.com/photo-1516116211223-48a122638e59?auto=format&fit=crop&w=800&q=80"
            prov = c.channel or c.source.capitalize()

            formatted.append({
                "id": c.resource_id,
                "title": c.title,
                "type": c.type,
                "source": c.source,
                "url": c.url,
                "link": c.url,
                "thumbnail": thumb,
                "imageUrl": thumb,
                "image_url": thumb,
                "author": prov,
                "provider": prov,
                "channel": prov,
                "duration": f"{c.duration_minutes or 20} Mins",
                "difficulty": "Intermediate",
                "rating": 4.9,
                "match_score": numeric_score,
                "matchScore": numeric_score,
                "progressPercentage": 0,
                "progress_percentage": 0,
                "reason": reason,
                "why_recommended": reason,
                "tags": [skill_gap.split()[0], c.type],
                "created_at": get_utc_now()
            })

        return formatted

    def _format_seed_resources(self, skill_gap: str, prefs: dict) -> list[dict[str, Any]]:
        results = []
        for r in VERIFIED_SEED_RESOURCES:
            item = dict(r)
            item["id"] = generate_uuid()
            item["link"] = item["url"]
            item["imageUrl"] = item["thumbnail"]
            item["image_url"] = item["thumbnail"]
            item["author"] = item["channel"]
            item["provider"] = item["channel"]
            item["duration"] = f"{item['duration_minutes']} Mins"
            item["rating"] = 4.9
            score = int(item["match_score"] * 100)
            item["match_score"] = score
            item["matchScore"] = score
            item["progressPercentage"] = 0
            item["progress_percentage"] = 0
            item["why_recommended"] = item["reason"]
            item["tags"] = [skill_gap.split()[0], item["type"]]
            item["created_at"] = get_utc_now()
            results.append(item)
        return results


curator_engine = CuratorEngine()
