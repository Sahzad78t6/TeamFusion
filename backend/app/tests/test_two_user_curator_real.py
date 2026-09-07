"""
Two-User Reality Verification Test — GrowthOS Phase 7
Proves that Learning Curator is genuinely real, user-specific, isolated,
and free of static seed fallbacks.
"""
import pytest
from unittest.mock import patch, AsyncMock
from app.agents.learning_curator.agent import learning_curator_agent
from app.database.repositories.user_repository import user_repository
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.recommendation_repository import recommendation_repository
from app.database.repositories.agent_run_repository import agent_run_repository
from app.services.search_providers.base import SearchResult
from app.exceptions import YouTubeQuotaExceededError


@pytest.mark.asyncio
async def test_two_user_distinct_curation_and_agent_run():
    user_a_id = "test_user_ml_engineer_001"
    user_b_id = "test_user_frontend_dev_002"

    # 1. Setup User A: Machine Learning Engineer
    await user_repository.save_profile(user_a_id, {
        "email": "user_a_ml@example.com",
        "name": "User A (ML Engineer)",
        "dreamRole": "Machine Learning Engineer"
    })
    await identity_repository.create_or_update(user_a_id, {
        "target_role": "Machine Learning Engineer",
        "skills": ["Python", "Machine Learning", "Pandas", "Scikit-learn"],
        "skill_gaps": [{"skill": "Neural Networks & Deep Learning", "severity": 0.85}],
        "learning_style": "practical"
    })

    # 2. Setup User B: Frontend Developer
    await user_repository.save_profile(user_b_id, {
        "email": "user_b_fe@example.com",
        "name": "User B (Frontend Developer)",
        "dreamRole": "Frontend Developer"
    })
    await identity_repository.create_or_update(user_b_id, {
        "target_role": "Frontend Developer",
        "skills": ["HTML", "CSS", "JavaScript", "React"],
        "skill_gaps": [{"skill": "React Server Components & Next.js", "severity": 0.90}],
        "learning_style": "visual"
    })

    # 3. Mock YouTube search provider returning distinct real search candidates per query
    async def mock_search(query: str, max_results: int = 6, filters=None):
        q = query.lower()
        if "machine learning" in q or "neural" in q or "python" in q or "scikit" in q:
            return [
                SearchResult(
                    resource_id="yt_ml_01",
                    title="Deep Learning with PyTorch and Scikit-learn",
                    url="https://www.youtube.com/watch?v=ml_pytorch_real",
                    description="Comprehensive guide to deep learning and neural network architectures.",
                    source="youtube",
                    type="video",
                    thumbnail="https://i.ytimg.com/vi/ml_pytorch_real/hqdefault.jpg",
                    channel="ML Engineering Daily",
                    duration_minutes=35
                ),
                SearchResult(
                    resource_id="yt_ml_02",
                    title="Machine Learning Foundations & Scikit-learn Pipelines",
                    url="https://www.youtube.com/watch?v=ml_sklearn_real",
                    description="Build production pipelines with Scikit-learn.",
                    source="youtube",
                    type="video",
                    thumbnail="https://i.ytimg.com/vi/ml_sklearn_real/hqdefault.jpg",
                    channel="Data Science Academy",
                    duration_minutes=25
                )
            ]
        elif "frontend" in q or "react" in q or "next.js" in q or "javascript" in q:
            return [
                SearchResult(
                    resource_id="yt_fe_01",
                    title="React Server Components and Architecture Guide",
                    url="https://www.youtube.com/watch?v=fe_react_real",
                    description="Mastering React server components and modern web layout patterns.",
                    source="youtube",
                    type="video",
                    thumbnail="https://i.ytimg.com/vi/fe_react_real/hqdefault.jpg",
                    channel="React Core Insights",
                    duration_minutes=28
                ),
                SearchResult(
                    resource_id="yt_fe_02",
                    title="Advanced Next.js 15 & React Performance Optimization",
                    url="https://www.youtube.com/watch?v=fe_nextjs_real",
                    description="Full production guide to frontend state and rendering.",
                    source="youtube",
                    type="video",
                    thumbnail="https://i.ytimg.com/vi/fe_nextjs_real/hqdefault.jpg",
                    channel="Frontend Mastery",
                    duration_minutes=40
                )
            ]
        return []

    with patch("app.services.search_providers.youtube_provider.youtube_provider.search", side_effect=mock_search):
        with patch("app.services.search_providers.web_provider.web_provider.search", return_value=[]):
            # 4. Execute Learning Curator for User A
            res_a = await learning_curator_agent.execute({"user_id": user_a_id})
            assert res_a.success is True
            data_a = res_a.data
            run_id_a = data_a.get("curation_run_id") or data_a.get("agent_run_id")
            assert run_id_a is not None

            # 5. Execute Learning Curator for User B
            res_b = await learning_curator_agent.execute({"user_id": user_b_id})
            assert res_b.success is True
            data_b = res_b.data
            run_id_b = data_b.get("curation_run_id") or data_b.get("agent_run_id")
            assert run_id_b is not None

            # 6. Verify run IDs are distinct
            assert run_id_a != run_id_b

            # 7. Verify recommendations are meaningfully different
            recs_a = data_a.get("recommendations", [])
            recs_b = data_b.get("recommendations", [])
            assert len(recs_a) > 0
            assert len(recs_b) > 0

            urls_a = {r["url"] for r in recs_a}
            urls_b = {r["url"] for r in recs_b}

            # 0% OVERLAP: User A (ML) and User B (Frontend) have completely disjoint recommendations!
            assert urls_a.isdisjoint(urls_b), f"Overlap detected between User A and User B: {urls_a.intersection(urls_b)}"
            assert any("ml_" in u for u in urls_a)
            assert any("fe_" in u for u in urls_b)

            # 8. Verify Phase 9 MongoDB User Ownership & Scoping
            stored_a = await recommendation_repository.get_by_user(user_a_id)
            stored_b = await recommendation_repository.get_by_user(user_b_id)
            assert stored_a is not None
            assert stored_b is not None
            assert stored_a["user_id"] == user_a_id
            assert stored_b["user_id"] == user_b_id

            # Verify every recommendation document contains required Phase 9 fields
            for r in stored_a["recommendations"]:
                assert r["user_id"] == user_a_id
                assert r["agent_run_id"] == run_id_a
                assert "title" in r
                assert "url" in r
                assert "query" in r
                assert "match_score" in r
                assert "reason" in r
                assert "status" in r
                assert "created_at" in r

            # 9. Verify Phase 5 & 6 AgentRun Telemetry
            run_doc_a = await agent_run_repository.get_run_by_id(run_id_a)
            run_doc_b = await agent_run_repository.get_run_by_id(run_id_b)
            assert run_doc_a is not None
            assert run_doc_b is not None

            assert run_doc_a["user_id"] == user_a_id
            assert run_doc_a["agent"] == "learning_curator"
            assert run_doc_a["execution_mode"] == "REAL"
            assert run_doc_a["status"] == "completed"
            assert run_doc_a["provider"] == "youtube"
            assert run_doc_a["results_retrieved"] > 0
            assert run_doc_a["results_selected"] > 0
            assert "recommendations" in run_doc_a["database_writes"]

            assert run_doc_b["user_id"] == user_b_id
            assert run_doc_b["execution_mode"] == "REAL"
            assert run_doc_b["status"] == "completed"


@pytest.mark.asyncio
async def test_zero_silent_fallback_on_quota_exceeded():
    """Verify that when YouTube quota is exceeded, agent raises error and records FAILED in AgentRun."""
    test_user_id = "test_user_quota_fail_003"
    await user_repository.save_profile(test_user_id, {
        "email": "quota_fail@example.com",
        "name": "Quota Fail User"
    })
    await identity_repository.create_or_update(test_user_id, {
        "target_role": "Python Developer",
        "skills": ["Python"]
    })

    with patch(
        "app.services.search_providers.youtube_provider.youtube_provider.search",
        side_effect=YouTubeQuotaExceededError("YOUTUBE_QUOTA_EXCEEDED: Quota exhausted")
    ):
        with pytest.raises(YouTubeQuotaExceededError):
            await learning_curator_agent.execute({"user_id": test_user_id})

        # Verify that run record in MongoDB reflects failure, NOT a fake fallback
        latest_run = await agent_run_repository.get_latest_run(test_user_id, "learning_curator")
        assert latest_run is not None
        assert latest_run["status"] == "failed"
        assert latest_run["execution_mode"] == "FAILED"
        assert "YOUTUBE_QUOTA_EXCEEDED" in latest_run["error"]

        # Verify NO fake recommendations were written to MongoDB for this user
        recs = await recommendation_repository.get_by_user(test_user_id)
        assert recs is None


@pytest.mark.asyncio
async def test_debug_endpoint_agent_run():
    """Verify GET /api/agents/runs/{agent_run_id} matches Phase 6 specification."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.services.auth_service import auth_service

    test_user_id = "test_user_debug_004"
    token = auth_service.create_access_token({"sub": test_user_id, "role": "STUDENT"})

    # Record a test run
    doc = await agent_run_repository.start_run(
        user_id=test_user_id,
        agent_name="learning_curator",
        input_context_summary={"target_role": "Machine Learning Engineer", "primary_gap": "Scikit-learn"},
        execution_mode="REAL"
    )
    run_id = doc["id"]
    await agent_run_repository.complete_run(
        run_id=run_id,
        status="completed",
        execution_mode="REAL",
        tools_called=["youtube_search"],
        queries=["machine learning scikit learn beginner"],
        provider="youtube",
        results_retrieved=25,
        results_selected=5,
        decision_summary="Selected top 5 machine learning tutorials",
        database_writes=["recommendations"]
    )

    client = TestClient(app)
    resp = client.get(f"/api/agents/runs/{run_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()

    assert data["agent"] == "learning_curator"
    assert data["user_id"] == test_user_id
    assert data["execution_mode"] == "REAL"
    assert data["status"] == "completed"
    assert data["tools_called"] == ["youtube_search"]
    assert data["provider"] == "youtube"
    assert data["query"] == "machine learning scikit learn beginner"
    assert data["results_retrieved"] == 25
    assert data["results_selected"] == 5
    assert data["database_writes"] == ["recommendations"]
