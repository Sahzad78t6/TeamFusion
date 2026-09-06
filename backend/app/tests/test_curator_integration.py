import pytest
from unittest.mock import AsyncMock, patch
from app.agents.supervisor.agent import supervisor_agent
from app.agents.learning_curator.agent import learning_curator_agent
from app.services.search_providers.base import SearchResult


@pytest.mark.asyncio
async def test_learning_curator_full_integration_flow():
    user_id = "student_integration_user"
    
    mock_yt_results = [
        SearchResult(
            resource_id="yt_feat_eng",
            title="Feature Engineering for Machine Learning Tutorial",
            url="https://www.youtube.com/watch?v=feat_12345",
            description="Complete practical guide to feature scaling, one-hot encoding, and feature selection.",
            source="youtube",
            type="video",
            thumbnail="https://i.ytimg.com/vi/feat_12345/hqdefault.jpg",
            channel="ML Masterclass",
            duration_minutes=32
        )
    ]

    mock_web_results = [
        SearchResult(
            resource_id="web_scikit_prep",
            title="Preprocessing Data - Scikit-Learn Guide",
            url="https://scikit-learn.org/stable/modules/preprocessing.html",
            description="Official guide on feature transformation, normalization, and feature extraction.",
            source="web",
            type="article",
            channel="Scikit-Learn",
            duration_minutes=25
        )
    ]

    with patch("app.services.search_providers.youtube_provider.youtube_provider.search", new_callable=AsyncMock) as mock_yt_search:
        with patch("app.services.search_providers.web_provider.web_provider.search", new_callable=AsyncMock) as mock_web_search:
            mock_yt_search.return_value = mock_yt_results
            mock_web_search.return_value = mock_web_results

            # 1. Ask Supervisor to find resources for Feature Engineering
            supervisor_res = await supervisor_agent.execute({
                "user_id": user_id,
                "message": "Find me resources to learn Feature Engineering for my ML Engineer goal."
            })

            assert supervisor_res.success is True
            assert supervisor_res.data["routed_to"] == "learning_curator"

            # 2. Directly invoke Learning Curator Agent
            curator_res = await learning_curator_agent.execute({
                "user_id": user_id,
                "topic": "Feature Engineering"
            })

            assert curator_res.success is True
            data = curator_res.data
            assert "resources" in data or "recommendations" in data
            resources = data.get("resources") or data.get("recommendations", [])
            assert len(resources) > 0

            # Verify no fabricated URLs and valid ranking output
            top_rec = resources[0]
            assert "youtube.com/watch?v=" in top_rec["url"] or "scikit-learn.org" in top_rec["url"]
            assert top_rec["match_score"] >= 80
            assert "reason" in top_rec or "why_recommended" in top_rec
