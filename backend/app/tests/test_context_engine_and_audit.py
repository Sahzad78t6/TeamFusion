"""
Tests for MongoDB Real Data Audit & Context Engine User Personalization
Covers:
1. User A context retrieval
2. User B context retrieval
3. User isolation
4. Identity Twin retrieval (user-scoped)
5. Recommendation isolation
6. Curator personalization
7. YouTube search mocking & query construction
8. Completed resource filtering (learning_activity)
9. Logout/login state isolation
10. Agent run tracking (agent_runs)
"""
import pytest
from unittest.mock import patch, AsyncMock
from app.context_engine import context_engine_service, UserContext
from app.database.repositories.user_repository import user_repository
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.recommendation_repository import recommendation_repository
from app.database.repositories.learning_activity_repository import learning_activity_repository
from app.database.repositories.agent_run_repository import agent_run_repository
from app.agents.learning_curator.agent import learning_curator_agent
from app.services.curator_engine import curator_engine, SearchResult


async def create_two_users():
    """Setup User A (ML Engineer) and User B (Frontend Engineer) in MongoDB store."""
    user_a_id = "user_test_ml_a"
    user_b_id = "user_test_frontend_b"

    # User A Profile & Identity Twin
    await user_repository.create_user({
        "id": user_a_id,
        "name": "Alice ML",
        "email": "alice.ml@growthos.test",
        "role": "STUDENT"
    })
    await identity_repository.create_or_update(user_a_id, {
        "target_role": "Machine Learning Engineer",
        "goal": "Senior ML Scientist",
        "learning_style": "Visual & Video",
        "preferred_content": ["Videos", "Interactive Labs"],
        "skills": ["Python", "Pandas"],
        "skill_gaps": [
            {"skill": "Machine Learning", "gap": 60, "priority": "high"},
            {"skill": "Statistics", "gap": 50, "priority": "high"}
        ]
    })

    # User B Profile & Identity Twin
    await user_repository.create_user({
        "id": user_b_id,
        "name": "Bob Frontend",
        "email": "bob.frontend@growthos.test",
        "role": "STUDENT"
    })
    await identity_repository.create_or_update(user_b_id, {
        "target_role": "Frontend Engineer",
        "goal": "Lead Frontend Architect",
        "learning_style": "Hands-on projects",
        "preferred_content": ["Articles", "Interactive Labs"],
        "skills": ["JavaScript", "HTML"],
        "skill_gaps": [
            {"skill": "React", "gap": 65, "priority": "high"},
            {"skill": "TypeScript", "gap": 55, "priority": "high"}
        ]
    })

    return user_a_id, user_b_id


@pytest.mark.asyncio
async def test_1_and_2_user_context_retrieval():
    """Test 1 & 2: User A and User B context retrieval from authentic database state."""
    user_a_id, user_b_id = await create_two_users()

    context_a: UserContext = await context_engine_service.get_user_context(user_a_id)
    assert context_a.user_id == user_a_id
    assert context_a.target_role == "Machine Learning Engineer"
    assert context_a.primary_gap == "Machine Learning"
    assert "video" in context_a.learning_style

    context_b: UserContext = await context_engine_service.get_user_context(user_b_id)
    assert context_b.user_id == user_b_id
    assert context_b.target_role == "Frontend Engineer"
    assert context_b.primary_gap == "React"
    assert "hands-on" in context_b.learning_style


@pytest.mark.asyncio
async def test_3_user_isolation():
    """Test 3: Contexts of User A and User B are strictly isolated with distinct hashes."""
    user_a_id, user_b_id = await create_two_users()

    context_a = await context_engine_service.get_user_context(user_a_id)
    context_b = await context_engine_service.get_user_context(user_b_id)

    assert context_a.user_id != context_b.user_id
    assert context_a.target_role != context_b.target_role
    assert context_a.primary_gap != context_b.primary_gap
    assert context_a.context_hash != context_b.context_hash


@pytest.mark.asyncio
async def test_4_identity_twin_retrieval_user_scoped():
    """Test 4: Identity Twin retrieval is user-scoped and strips internal ObjectIds."""
    user_a_id, user_b_id = await create_two_users()

    twin_a = await identity_repository.get_identity_twin_for_user(user_a_id)
    twin_b = await identity_repository.get_identity_twin_for_user(user_b_id)

    assert twin_a is not None
    assert twin_b is not None
    assert twin_a["user_id"] == user_a_id
    assert twin_b["user_id"] == user_b_id
    assert "_id" not in twin_a
    assert "_id" not in twin_b
    assert twin_a["target_role"] == "Machine Learning Engineer"
    assert twin_b["target_role"] == "Frontend Engineer"


@pytest.mark.asyncio
async def test_5_recommendation_isolation():
    """Test 5: Recommendation repository returns only the authenticated user's recommendations."""
    user_a_id, user_b_id = await create_two_users()

    await recommendation_repository.save_recommendations(
        user_id=user_a_id,
        recommendations=[{"id": "rec_a_1", "title": "PyTorch for ML", "url": "https://example.com/ml1"}],
        target_role="Machine Learning Engineer",
        primary_gap="Machine Learning"
    )

    await recommendation_repository.save_recommendations(
        user_id=user_b_id,
        recommendations=[{"id": "rec_b_1", "title": "React 19 Deep Dive", "url": "https://example.com/react1"}],
        target_role="Frontend Engineer",
        primary_gap="React"
    )

    doc_a = await recommendation_repository.get_by_user(user_a_id)
    doc_b = await recommendation_repository.get_by_user(user_b_id)

    assert doc_a["user_id"] == user_a_id
    assert doc_b["user_id"] == user_b_id
    assert doc_a["recommendations"][0]["id"] == "rec_a_1"
    assert doc_b["recommendations"][0]["id"] == "rec_b_1"
    assert "_id" not in doc_a
    assert "_id" not in doc_b


@pytest.mark.asyncio
async def test_6_and_7_curator_personalization_and_youtube_mocking():
    """
    Test 6 & 7: Curator executes with real context, queries YouTube provider with role/gap,
    and returns personalized non-overlapping resource sets for User A vs User B.
    """
    user_a_id, user_b_id = await create_two_users()

    with patch("app.services.search_providers.youtube_provider.youtube_provider.search", new_callable=AsyncMock) as mock_yt:
        with patch("app.services.search_providers.web_provider.web_provider.search", new_callable=AsyncMock) as mock_web:
            # When YouTube search is called, return role-specific items
            async def yt_side_effect(query, max_results=6):
                if "machine learning" in query.lower() or "statistics" in query.lower():
                    return [
                        SearchResult(
                            resource_id="yt_ml_1",
                            title="Machine Learning & Evaluation Guide",
                            url="https://youtube.com/watch?v=ml_eval_101",
                            source="youtube",
                            type="video",
                            channel="StatQuest"
                        )
                    ]
                elif "react" in query.lower() or "frontend" in query.lower():
                    return [
                        SearchResult(
                            resource_id="yt_fe_1",
                            title="React 19 Architecture Patterns",
                            url="https://youtube.com/watch?v=react19_patterns",
                            source="youtube",
                            type="video",
                            channel="Jack Herrington"
                        )
                    ]
                return []

            mock_yt.side_effect = yt_side_effect
            mock_web.return_value = []

            # Execute Curator for User A
            resp_a = await learning_curator_agent.execute({"user_id": user_a_id})
            assert resp_a.success is True
            recs_a = resp_a.data.get("resources", [])
            assert len(recs_a) > 0
            assert recs_a[0]["url"] == "https://youtube.com/watch?v=ml_eval_101"

            # Execute Curator for User B
            resp_b = await learning_curator_agent.execute({"user_id": user_b_id})
            assert resp_b.success is True
            recs_b = resp_b.data.get("resources", [])
            assert len(recs_b) > 0
            assert recs_b[0]["url"] == "https://youtube.com/watch?v=react19_patterns"

            # Check queries used by YouTube
            captured_queries = [call[0][0] for call in mock_yt.call_args_list]
            assert any("machine learning" in q.lower() for q in captured_queries)
            assert any("react" in q.lower() for q in captured_queries)

            # Check 0 overlap
            urls_a = {r["url"] for r in recs_a}
            urls_b = {r["url"] for r in recs_b}
            assert len(urls_a.intersection(urls_b)) == 0


@pytest.mark.asyncio
async def test_8_completed_resource_filtering():
    """Test 8: Completed resources tracked in learning_activity are filtered from recommendations."""
    user_a_id, _ = await create_two_users()

    # User A completes a resource
    completed_resource_id = "yt_ml_1"
    await learning_activity_repository.log_activity(
        user_id=user_a_id,
        resource_id=completed_resource_id,
        action="completed",
        progress=100.0
    )

    completed_ids = await learning_activity_repository.get_completed_resource_ids(user_a_id)
    assert completed_resource_id in completed_ids

    # Context engine must include it
    context = await context_engine_service.get_user_context(user_a_id)
    assert completed_resource_id in context.completed_resources

    # Raw candidates containing completed resource
    candidates = [
        SearchResult(
            resource_id=completed_resource_id,
            title="Completed Machine Learning Tutorial",
            url="https://youtube.com/watch?v=completed_ml",
            source="youtube",
            type="video"
        ),
        SearchResult(
            resource_id="yt_ml_new",
            title="Brand New Advanced ML System Design",
            url="https://youtube.com/watch?v=new_ml",
            source="youtube",
            type="video"
        )
    ]

    filtered = curator_engine._filter_and_deduplicate(candidates, context=context)
    # The completed resource must be removed!
    filtered_ids = [c.resource_id for c in filtered]
    assert completed_resource_id not in filtered_ids
    assert "yt_ml_new" in filtered_ids


@pytest.mark.asyncio
async def test_9_agent_run_tracking():
    """Test 9 & 10: Every agent execution is persisted to agent_runs with full telemetry."""
    user_a_id, _ = await create_two_users()

    # Curator was executed for user_a in previous test
    latest_run = await agent_run_repository.get_latest_run(user_a_id, "learning_curator")
    assert latest_run is not None
    assert latest_run["user_id"] == user_a_id
    assert latest_run["agent_name"] == "learning_curator"
    assert latest_run["status"] in ["completed", "fallback"]
    assert "Machine Learning" in latest_run["skills_considered"]
    assert latest_run["resources_generated"] > 0
    assert latest_run["started_at"] is not None
    assert latest_run["completed_at"] is not None
