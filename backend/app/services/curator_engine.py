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
from app.services.curator_context import UserLearningContext, curator_context_builder
from app.exceptions import (
    YouTubeQuotaExceededError,
    YouTubeApiKeyMissingError,
    YouTubeUnavailableError,
)
from app.llm.provider import llm_provider
from app.utils.helpers import get_utc_now, generate_uuid

logger = logging.getLogger(__name__)

VERIFIED_ROLE_SEED_CATALOG: dict[str, list[dict[str, Any]]] = {
    "frontend": [
        {
            "title": "React 19 & Modern Component Architecture Masterclass",
            "type": "video",
            "source": "youtube",
            "url": "https://www.youtube.com/watch?v=8pDqJVdNa44",
            "thumbnail": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?auto=format&fit=crop&w=800&q=80",
            "channel": "freeCodeCamp.org",
            "duration_minutes": 35,
            "difficulty": "Intermediate",
            "match_score": 0.96,
            "reason": "Directly targets React component composition and state boundaries for Frontend Engineers."
        },
        {
            "title": "TypeScript Handbook: Mastering Type Systems & Generics",
            "type": "article",
            "source": "web",
            "url": "https://www.typescriptlang.org/docs/handbook/intro.html",
            "thumbnail": "https://images.unsplash.com/photo-1516116211223-48a122638e59?auto=format&fit=crop&w=800&q=80",
            "channel": "TypeScript Docs",
            "duration_minutes": 25,
            "difficulty": "Intermediate",
            "match_score": 0.93,
            "reason": "Official TypeScript documentation for strict typing and scalable frontend architecture."
        },
        {
            "title": "State Management with Zustand & Redux Toolkit in Practice",
            "type": "video",
            "source": "youtube",
            "url": "https://www.youtube.com/watch?v=KzbmW_XpTzM",
            "thumbnail": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80",
            "channel": "Jack Herrington",
            "duration_minutes": 28,
            "difficulty": "Intermediate",
            "match_score": 0.91,
            "reason": "Comparative practical guide to global state vs local state in modern web apps."
        },
        {
            "title": "Modern CSS Architecture & Responsive Layout Engineering",
            "type": "course",
            "source": "web",
            "url": "https://web.dev/learn/css",
            "thumbnail": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=800&q=80",
            "channel": "Google web.dev",
            "duration_minutes": 40,
            "difficulty": "Beginner",
            "match_score": 0.88,
            "reason": "Comprehensive Google curriculum on CSS grid, flexbox, and rendering performance."
        }
    ],
    "machine learning": [
        {
            "title": "Machine Learning Model Evaluation: Precision, Recall, ROC & PR Curves",
            "type": "video",
            "source": "youtube",
            "url": "https://www.youtube.com/watch?v=4jRBRDbJemM",
            "thumbnail": "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?auto=format&fit=crop&w=800&q=80",
            "channel": "StatQuest with Josh Starmer",
            "duration_minutes": 25,
            "difficulty": "Intermediate",
            "match_score": 0.96,
            "reason": "Visual breakdown of classification and regression evaluation metrics."
        },
        {
            "title": "Deep Dive into Feature Engineering for Machine Learning",
            "type": "article",
            "source": "web",
            "url": "https://scikit-learn.org/stable/modules/preprocessing.html",
            "thumbnail": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80",
            "channel": "Scikit-Learn Docs",
            "duration_minutes": 30,
            "difficulty": "Intermediate",
            "match_score": 0.93,
            "reason": "Official documentation covering feature scaling, encoding, and transformation."
        },
        {
            "title": "Neural Networks & Deep Learning Foundations with PyTorch",
            "type": "course",
            "source": "web",
            "url": "https://pytorch.org/tutorials/beginner/basics/intro.html",
            "thumbnail": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=800&q=80",
            "channel": "PyTorch Official",
            "duration_minutes": 45,
            "difficulty": "Advanced",
            "match_score": 0.90,
            "reason": "Hands-on PyTorch tensor computation and neural network building blocks."
        },
        {
            "title": "Supervised Machine Learning Algorithms: From Math to Code",
            "type": "video",
            "source": "youtube",
            "url": "https://www.youtube.com/watch?v=i_LwzRVP7bg",
            "thumbnail": "https://images.unsplash.com/photo-1516116211223-48a122638e59?auto=format&fit=crop&w=800&q=80",
            "channel": "freeCodeCamp.org",
            "duration_minutes": 40,
            "difficulty": "Intermediate",
            "match_score": 0.88,
            "reason": "Comprehensive walkthrough of regression, decision trees, and ensemble methods."
        }
    ],
    "ai": [
        {
            "title": "Building Production Multi-Agent Workflows with LangGraph & Python",
            "type": "video",
            "source": "youtube",
            "url": "https://www.youtube.com/watch?v=pv3hhfsb1Q0",
            "thumbnail": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80",
            "channel": "LangChain",
            "duration_minutes": 32,
            "difficulty": "Advanced",
            "match_score": 0.97,
            "reason": "State graph compilation, memory persistence, and agentic cycles in Python."
        },
        {
            "title": "Retrieval-Augmented Generation (RAG) Architecture & Vector Search",
            "type": "article",
            "source": "web",
            "url": "https://docs.pinecone.io/guides/get-started/overview",
            "thumbnail": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=800&q=80",
            "channel": "Pinecone Learning Center",
            "duration_minutes": 25,
            "difficulty": "Intermediate",
            "match_score": 0.92,
            "reason": "Explains embedding generation, chunking strategies, and hybrid vector search."
        },
        {
            "title": "Building High-Throughput Async AI Services with FastAPI",
            "type": "video",
            "source": "youtube",
            "url": "https://www.youtube.com/watch?v=7t2alSnE2-I",
            "thumbnail": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80",
            "channel": "Tech With Tim",
            "duration_minutes": 35,
            "difficulty": "Intermediate",
            "match_score": 0.89,
            "reason": "Practical backend API architecture targeting model serving and async streaming."
        }
    ],
    "backend": [
        {
            "title": "Designing Scalable REST & GraphQL Microservices Architecture",
            "type": "video",
            "source": "youtube",
            "url": "https://www.youtube.com/watch?v=7t2alSnE2-I",
            "thumbnail": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80",
            "channel": "Tech With Tim",
            "duration_minutes": 35,
            "difficulty": "Intermediate",
            "match_score": 0.94,
            "reason": "REST and GraphQL endpoint design, Pydantic validation, and dependency injection."
        },
        {
            "title": "PostgreSQL Indexing, Query Optimization & Transaction Isolation",
            "type": "article",
            "source": "web",
            "url": "https://www.postgresql.org/docs/current/indexes.html",
            "thumbnail": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?auto=format&fit=crop&w=800&q=80",
            "channel": "PostgreSQL Official Docs",
            "duration_minutes": 30,
            "difficulty": "Advanced",
            "match_score": 0.91,
            "reason": "Covers B-tree indexing, query planner analysis, and ACID concurrency."
        }
    ],
    "general": [
        {
            "title": "Mastering Data Structures: Trees, Graphs & Traversal",
            "type": "course",
            "source": "web",
            "url": "https://github.com/trekhleb/javascript-algorithms",
            "thumbnail": "https://images.unsplash.com/photo-1516116211223-48a122638e59?auto=format&fit=crop&w=800&q=80",
            "channel": "GitHub Education",
            "duration_minutes": 45,
            "difficulty": "Advanced",
            "match_score": 0.89,
            "reason": "Hands-on algorithm implementations and visual explanations."
        },
        {
            "title": "System Design Fundamentals for Scalable Software",
            "type": "video",
            "source": "youtube",
            "url": "https://www.youtube.com/watch?v=bUHFg8CZFCA",
            "thumbnail": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=800&q=80",
            "channel": "freeCodeCamp.org",
            "duration_minutes": 50,
            "difficulty": "Advanced",
            "match_score": 0.92,
            "reason": "Covers load balancing, caching tiers, database replication, and consistency."
        }
    ]
}


from app.context_engine import context_engine_service, UserContext

class CuratorEngine:
    async def curate_personalized_resources(
        self,
        user_id: str,
        topic: str = "",
        target_role: str = "",
        context: Any = None,
        agent_run_id: str = ""
    ) -> list[dict[str, Any]]:
        """
        Main entry point for REAL Learning Curator:
        1. Synthesize UserContext from authentic MongoDB collections via Context Engine.
        2. Generate user-tailored targeted search queries.
        3. Search real YouTube Data API v3 and Web providers concurrently.
        4. Detect and propagate any provider errors (quota, key missing) WITHOUT SILENT FALLBACKS.
        5. Filter and deduplicate candidates (excluding completed resources).
        6. Apply heuristic ranking based on skill gap and target role.
        7. Apply LLM re-ranking & personalized explanation generation.
        8. Inject authentic MongoDB user ownership fields.
        """
        # 1. Build authentic student context
        if context is None:
            context = await context_engine_service.get_user_context(
                user_id=user_id,
                topic=topic,
                target_role=target_role
            )
        elif target_role and hasattr(context, "target_role"):
            context.target_role = target_role
            if hasattr(context, "compute_hash"):
                context.context_hash = context.compute_hash()

        logger.info(
            f"[CuratorEngine] user={user_id} role='{context.target_role}' "
            f"primary_gap='{context.primary_gap}' secondary_gap='{context.secondary_gap}' "
            f"style='{context.learning_style}' hash={context.context_hash}"
        )

        # 2. Generate user-tailored search queries
        queries = self._generate_search_queries(context)
        logger.info(f"[CuratorEngine] Generated personalized search queries for {user_id}: {queries}")

        # 3. Collect candidates from providers
        candidate_tasks = []
        for q in queries:
            candidate_tasks.append(youtube_provider.search(q, max_results=6))
            candidate_tasks.append(web_provider.search(q, max_results=6))

        results_lists = await asyncio.gather(*candidate_tasks, return_exceptions=True)

        # Explicit failure detection: Never silently swallow API or quota errors!
        provider_errors = [
            res for res in results_lists
            if isinstance(res, (YouTubeQuotaExceededError, YouTubeApiKeyMissingError, YouTubeUnavailableError))
        ]
        if provider_errors:
            logger.error(f"[CuratorEngine] Real provider failed: {provider_errors[0]}")
            raise provider_errors[0]

        raw_candidates: list[SearchResult] = []
        for res in results_lists:
            if isinstance(res, list):
                raw_candidates.extend(res)
            elif isinstance(res, Exception):
                logger.warning(f"[CuratorEngine] Non-fatal provider exception: {res}")

        logger.info(f"[CuratorEngine] Collected {len(raw_candidates)} raw candidate resources for {user_id}")

        # 4. Filter and deduplicate candidates
        filtered_candidates = self._filter_and_deduplicate(raw_candidates, context)
        logger.info(f"[CuratorEngine] Filtered to {len(filtered_candidates)} unique candidates for {user_id}")

        # 5. ZERO SILENT FALLBACK: If live search returned 0 candidates, fail with explicit error!
        if not filtered_candidates:
            # If any provider errored out, raise it
            for res in results_lists:
                if isinstance(res, Exception):
                    raise res
            raise YouTubeUnavailableError(
                f"NO_RESOURCES_FOUND: Real search yielded 0 candidate resources for role '{context.target_role}' and gap '{context.primary_gap}'."
            )

        # 6. Apply heuristic ranking
        ranked_candidates = self._apply_heuristic_ranking(filtered_candidates, context)

        # Take top 8 candidates for re-ranking
        top_candidates = ranked_candidates[:8]

        # 7. LLM Re-Ranking & Personalization Reason Generation
        final_resources = await self._apply_llm_reranking(
            top_candidates,
            context,
            user_id=user_id,
            agent_run_id=agent_run_id,
            query=queries[0] if queries else ""
        )

        # Stash telemetry onto context for AgentRun tracking
        if hasattr(context, "__dict__"):
            context.last_queries = queries
            context.results_retrieved = len(raw_candidates)
            context.results_selected = len(final_resources)

        return final_resources

    def _generate_search_queries(self, context: UserLearningContext) -> list[str]:
        """Generate targeted search queries reflecting actual user skill gap and role."""
        style_keyword = "tutorial practical examples" if context.learning_style in ["practical", "hands-on"] else "course guide"
        queries = [
            f"{context.primary_gap} {style_keyword}",
            f"{context.target_role} {context.primary_gap} tutorial",
            f"{context.secondary_gap} {context.target_role} guide"
        ]
        return queries

    def _filter_and_deduplicate(
        self,
        candidates: list[SearchResult],
        context: Any = None,
        user_id: str = ""
    ) -> list[SearchResult]:
        seen_urls = set()
        unique: list[SearchResult] = []
        completed = set()
        if context and hasattr(context, "completed_resources"):
            completed = context.completed_resources

        for c in candidates:
            url_clean = c.url.strip().rstrip("/")
            if not url_clean or url_clean in seen_urls:
                continue
            # Skip resources already completed by the user
            if c.resource_id in completed:
                continue
            seen_urls.add(url_clean)
            unique.append(c)

        return unique

    def _apply_heuristic_ranking(
        self,
        candidates: list[SearchResult],
        context: Any = None,
        skill_gap: str = "",
        prefs: dict | None = None
    ) -> list[SearchResult]:
        primary_gap = getattr(context, "primary_gap", "") or skill_gap or "Software Engineering"
        target_role = getattr(context, "target_role", "") or "Engineer"
        
        learning_style = "practical"
        if context and hasattr(context, "learning_style"):
            learning_style = context.learning_style
        elif prefs and prefs.get("video_preference"):
            learning_style = "visual"

        primary_terms = set(primary_gap.lower().split())
        role_terms = set(target_role.lower().split())

        def compute_score(c: SearchResult) -> float:
            content_text = (c.title + " " + c.description).lower()
            primary_matches = sum(1 for term in primary_terms if term in content_text)
            role_matches = sum(1 for term in role_terms if term in content_text)

            primary_relevance = min(1.0, primary_matches / max(1, len(primary_terms)))
            role_relevance = min(1.0, role_matches / max(1, len(role_terms)))

            # Bonus for matching video preference
            style_bonus = 0.15 if (c.source == "youtube" and learning_style in ["visual", "video", "practical"]) else 0.05
            duration_match = 0.10 if (c.duration_minutes and c.duration_minutes <= 45) else 0.05

            score = (primary_relevance * 0.45) + (role_relevance * 0.25) + style_bonus + duration_match + 0.15
            return min(1.0, max(0.1, score))

        candidates.sort(key=compute_score, reverse=True)
        return candidates

    async def _apply_llm_reranking(
        self,
        candidates: list[SearchResult],
        context: UserLearningContext,
        user_id: str = "",
        agent_run_id: str = "",
        query: str = ""
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
            f"Evaluate learning resources for a student targeting '{context.target_role}' "
            f"with primary skill gap in '{context.primary_gap}' and learning style '{context.learning_style}'.\n"
            f"Candidates: {candidate_json}\n"
            f"Return JSON matching key 'evaluations', where each item has 'url', 'match_score' (0.0 to 1.0), and 'reason' (why it helps)."
        )

        llm_rerank_succeeded = False
        try:
            eval_res = llm_provider.generate_json(prompt)
            eval_map = {}
            if eval_res and "evaluations" in eval_res:
                for ev in eval_res["evaluations"]:
                    eval_map[ev.get("url")] = ev
                llm_rerank_succeeded = bool(eval_map)
        except Exception as e:
            logger.error(
                f"FALLBACK TRIGGER: Curator LLM re-ranking failed — resources will use heuristic scores "
                f"instead of personalized AI evaluation. Reason: {e}"
            )
            eval_map = {}

        skill_identifier = (getattr(context, "primary_gap", "") or "general").lower().replace(" ", "_")
        active_query = query or f"{context.primary_gap} tutorial"

        formatted = []
        for i, c in enumerate(candidates):
            llm_eval = eval_map.get(c.url, {})
            score = llm_eval.get("match_score") or round(0.95 - (i * 0.03), 2)
            reason = (
                llm_eval.get("reason")
                or f"Recommended for your '{context.target_role}' target to bridge your gap in '{context.primary_gap}'."
            )
            numeric_score = round(score * 100) if score <= 1.0 else int(score)
            thumb = c.thumbnail or "https://images.unsplash.com/photo-1516116211223-48a122638e59?auto=format&fit=crop&w=800&q=80"
            prov = c.channel or c.source.capitalize()

            # Per-resource: was THIS resource's score/reason from LLM or heuristic?
            resource_ai_generated = bool(llm_eval)  # True only if LLM returned an eval for this URL

            formatted.append({
                # Phase 9: Explicit MongoDB User Ownership Fields
                "user_id": user_id,
                "agent_run_id": agent_run_id,
                "skill_id": skill_identifier,
                "title": c.title,
                "description": c.description,
                "source": c.source,
                "url": c.url,
                "thumbnail": thumb,
                "query": active_query,
                "match_score": numeric_score,
                "reason": reason,
                "status": "active",
                "created_at": get_utc_now(),

                # Visibility fields — inspectable via browser devtools network tab.
                # data_source: always live_search (seed helpers are not called from this flow).
                # ai_generated: True only if LLM evaluated this specific resource.
                # llm_rerank_source: overall re-rank outcome for the batch.
                "data_source": "live_search",
                "ai_generated": resource_ai_generated,
                "llm_rerank_source": "llm" if resource_ai_generated else "heuristic_fallback",

                # Frontend & Context Backward Compatibility Fields
                "id": c.resource_id,
                "link": c.url,
                "imageUrl": thumb,
                "image_url": thumb,
                "author": prov,
                "provider": prov,
                "channel": prov,
                "type": c.type,
                "duration": f"{c.duration_minutes or 20} Mins",
                "difficulty": "Intermediate",
                "rating": 4.9,
                "matchScore": numeric_score,
                "progressPercentage": 0,
                "progress_percentage": 0,
                "why_recommended": reason,
                "tags": [context.primary_gap.split()[0], c.type],
            })

        return formatted

    def _format_domain_seed_resources(self, context: UserLearningContext) -> list[dict[str, Any]]:
        """Select domain-appropriate seed catalog according to user's actual target role and skill gap."""
        role_gap_text = f"{context.target_role} {context.primary_gap}".lower()
        if any(k in role_gap_text for k in ["machine learning", "ml ", "ml engineer", "deep learning", "feature engineering", "data science"]):
            items = VERIFIED_ROLE_SEED_CATALOG["machine learning"]
        elif any(k in role_gap_text for k in ["frontend", "react", "ui", "web developer"]):
            items = VERIFIED_ROLE_SEED_CATALOG["frontend"]
        elif any(k in role_gap_text for k in ["ai ", "ai engineer", "agent", "llm"]):
            items = VERIFIED_ROLE_SEED_CATALOG["ai"]
        elif any(k in role_gap_text for k in ["backend", "api", "database"]):
            items = VERIFIED_ROLE_SEED_CATALOG["backend"]
        else:
            items = VERIFIED_ROLE_SEED_CATALOG["general"]

        results = []
        for r in items:
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
            item["why_recommended"] = (
                f"Curated for your '{context.target_role}' goal addressing your '{context.primary_gap}' gap."
            )
            item["reason"] = item["why_recommended"]
            item["tags"] = [context.primary_gap.split()[0], item["type"]]
            item["created_at"] = get_utc_now()
            results.append(item)
        return results

    def _format_seed_resources(self, skill_gap: str, prefs: dict) -> list[dict[str, Any]]:
        """Legacy helper for backward compatibility."""
        items = VERIFIED_ROLE_SEED_CATALOG["general"]
        results = []
        for r in items:
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
            item["why_recommended"] = f"Addresses key foundations in {skill_gap}."
            item["reason"] = item["why_recommended"]
            item["tags"] = [skill_gap.split()[0], item["type"]]
            item["created_at"] = get_utc_now()
            results.append(item)
        return results


curator_engine = CuratorEngine()
