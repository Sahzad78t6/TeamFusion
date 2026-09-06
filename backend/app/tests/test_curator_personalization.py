import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.utils.jwt import create_access_token
from app.database.repositories.identity_repository import identity_repository
from app.database.repositories.user_repository import user_repository
from app.database.repositories.recommendation_repository import recommendation_repository
from app.services.curator_context import curator_context_builder


@pytest.mark.asyncio
async def test_curator_real_user_personalization_isolation():
    """
    Verifies that User A (Frontend Engineer) and User B (Machine Learning Engineer)
    receive genuinely distinct, domain-specific recommendations and cannot access each other's data.
    """
    client = TestClient(app)

    user_a_id = "user_frontend_alice"
    user_b_id = "user_ml_bob"

    # Setup User A profile & Identity Twin (Frontend Engineer)
    await identity_repository.create_or_update(user_a_id, {
        "user_id": user_a_id,
        "target_role": "Frontend Engineer",
        "goal": "Senior React & UI Architect",
        "skills": ["React", "JavaScript", "HTML", "CSS"],
        "skill_gaps": [
            {"skill": "TypeScript & Modern Web Standards", "gap": 55, "priority": "high"},
            {"skill": "State Management & Performance", "gap": 45, "priority": "high"}
        ],
        "learning_style": "practical"
    })

    # Setup User B profile & Identity Twin (ML Engineer)
    await identity_repository.create_or_update(user_b_id, {
        "user_id": user_b_id,
        "target_role": "Machine Learning Engineer",
        "goal": "Chief AI & Systems Scientist",
        "skills": ["Python", "FastAPI", "Pandas"],
        "skill_gaps": [
            {"skill": "Model Evaluation & Metrics", "gap": 60, "priority": "high"},
            {"skill": "Deep Learning & Neural Networks", "gap": 50, "priority": "high"}
        ],
        "learning_style": "visual"
    })

    token_a = create_access_token({"sub": user_a_id})
    token_b = create_access_token({"sub": user_b_id})

    # 1. Run Curator for User A
    resp_a = client.post("/recommendation/refresh", headers={"Authorization": f"Bearer {token_a}"})
    assert resp_a.status_code == 200
    data_a = resp_a.json()
    assert data_a["user_id"] == user_a_id
    assert "Frontend" in data_a.get("target_role", "")
    recs_a = data_a["recommendations"]
    assert len(recs_a) > 0

    # User A recommendations must match Frontend domain
    recs_a_text = " ".join([r["title"].lower() + " " + (r.get("why_recommended") or "").lower() for r in recs_a])
    assert any(k in recs_a_text for k in ["react", "typescript", "frontend", "css", "component", "state"])

    # 2. Run Curator for User B
    resp_b = client.post("/recommendation/refresh", headers={"Authorization": f"Bearer {token_b}"})
    assert resp_b.status_code == 200
    data_b = resp_b.json()
    assert data_b["user_id"] == user_b_id
    assert "Machine Learning" in data_b.get("target_role", "")
    recs_b = data_b["recommendations"]
    assert len(recs_b) > 0

    # User B recommendations must match ML domain
    recs_b_text = " ".join([r["title"].lower() + " " + (r.get("why_recommended") or "").lower() for r in recs_b])
    assert any(k in recs_b_text for k in ["machine learning", "model", "scikit", "evaluation", "neural", "pytorch", "feature engineering"])

    # 3. Verify Material Difference Between User A and User B
    urls_a = {r["url"] for r in recs_a}
    urls_b = {r["url"] for r in recs_b}
    # Sets of URLs should have zero or minimal overlap because their domains are Frontend vs ML
    overlap = urls_a.intersection(urls_b)
    assert len(overlap) < len(urls_a), "User A and User B received identical recommendations!"

    # 4. GET /recommendation Isolation
    get_a = client.get("/recommendation", headers={"Authorization": f"Bearer {token_a}"})
    assert get_a.status_code == 200
    assert get_a.json()["user_id"] == user_a_id

    get_b = client.get("/recommendation", headers={"Authorization": f"Bearer {token_b}"})
    assert get_b.status_code == 200
    assert get_b.json()["user_id"] == user_b_id


@pytest.mark.asyncio
async def test_curator_context_hash_invalidation_on_role_change():
    """
    Verifies that when a user updates their target role, GET /recommendation
    automatically detects a stale context hash and regenerates recommendations.
    """
    client = TestClient(app)
    user_id = "user_evolving_charlie"
    token = create_access_token({"sub": user_id})

    # Start as Backend Developer
    await identity_repository.create_or_update(user_id, {
        "user_id": user_id,
        "target_role": "Backend Engineer",
        "skills": ["Python", "FastAPI"],
        "skill_gaps": [{"skill": "PostgreSQL & Database Optimization", "gap": 50}],
    })

    init_resp = client.post("/recommendation/refresh", headers={"Authorization": f"Bearer {token}"})
    assert init_resp.status_code == 200
    init_data = init_resp.json()
    assert "Backend" in init_data["target_role"]
    init_hash = init_data["context_hash"]

    # Now change target role to Cybersecurity Specialist
    await identity_repository.create_or_update(user_id, {
        "user_id": user_id,
        "target_role": "Cybersecurity Specialist",
        "skills": ["Networking", "Linux"],
        "skill_gaps": [{"skill": "Network Security & Penetration Testing", "gap": 65}],
    })

    # Calling GET /recommendation should detect the stale context hash and regenerate
    updated_resp = client.get("/recommendation", headers={"Authorization": f"Bearer {token}"})
    assert updated_resp.status_code == 200
    updated_data = updated_resp.json()
    assert "Cybersecurity" in updated_data["target_role"]
    assert updated_data["context_hash"] != init_hash
