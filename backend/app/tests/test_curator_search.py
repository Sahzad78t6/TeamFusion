import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.search_providers.base import SearchResult
from app.services.search_providers.youtube_provider import YouTubeSearchProvider
from app.services.search_providers.web_provider import WebSearchProvider
from app.services.curator_engine import curator_engine


@pytest.mark.asyncio
async def test_youtube_search_provider_mock():
    provider = YouTubeSearchProvider(api_key="mock_key")
    
    mock_response = {
        "items": [
            {
                "id": {"videoId": "test_video_123"},
                "snippet": {
                    "title": "Python Recursion Explained",
                    "description": "Learn recursion in Python with visual diagrams.",
                    "channelTitle": "Code Academy",
                    "publishedAt": "2026-01-01T00:00:00Z"
                }
            }
        ]
    }

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value.read.return_value = str(mock_response).replace("'", '"').encode("utf-8")
        mock_urlopen.return_value = mock_cm

        results = await provider.search("python recursion", max_results=5)
        assert len(results) == 1
        assert results[0].url == "https://www.youtube.com/watch?v=test_video_123"
        assert results[0].source == "youtube"


@pytest.mark.asyncio
async def test_curator_engine_deduplication_and_ranking():
    candidates = [
        SearchResult(resource_id="1", title="Python Recursion", url="https://example.com/rec1", source="web", type="article"),
        SearchResult(resource_id="2", title="Python Recursion", url="https://example.com/rec1", source="web", type="article"), # Duplicate
        SearchResult(resource_id="3", title="Advanced Graph Traversal", url="https://example.com/rec2", source="youtube", type="video")
    ]

    filtered = curator_engine._filter_and_deduplicate(candidates, user_id="test_user")
    assert len(filtered) == 2

    ranked = curator_engine._apply_heuristic_ranking(filtered, skill_gap="Recursion", prefs={"video_preference": True})
    assert len(ranked) == 2
    assert ranked[0].url == "https://example.com/rec1" or ranked[0].source == "youtube"


@pytest.mark.asyncio
async def test_curator_raises_on_empty_search_without_fallback():
    from app.exceptions import YouTubeUnavailableError
    with patch("app.services.search_providers.youtube_provider.youtube_provider.search", new_callable=AsyncMock) as mock_yt:
        with patch("app.services.search_providers.web_provider.web_provider.search", new_callable=AsyncMock) as mock_web:
            mock_yt.return_value = []
            mock_web.return_value = []

            with pytest.raises(YouTubeUnavailableError) as exc_info:
                await curator_engine.curate_personalized_resources("user_fallback_test", topic="Feature Engineering")
            assert "NO_RESOURCES_FOUND" in str(exc_info.value)
