"""
YouTube Search Provider — GrowthOS Learning Curator
Fetches real YouTube educational videos via YouTube Data API v3.
"""
import logging
import urllib.parse
import urllib.request
import json
import asyncio
from typing import Any
from app.config.settings import settings
from app.services.search_providers.base import SearchProvider, SearchResult

logger = logging.getLogger(__name__)


class YouTubeSearchProvider(SearchProvider):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.YOUTUBE_API_KEY

    async def search(self, query: str, max_results: int = 15, filters: dict | None = None) -> list[SearchResult]:
        if not self.api_key or self.api_key.startswith("your_"):
            logger.info("YouTube API key not configured. YouTube provider returning empty candidates.")
            return []

        def _fetch_youtube_sync() -> list[SearchResult]:
            try:
                params = {
                    "part": "snippet",
                    "maxResults": min(max_results, 25),
                    "q": query,
                    "type": "video",
                    "safeSearch": "moderate",
                    "relevanceLanguage": "en",
                    "key": self.api_key
                }
                url = f"https://www.googleapis.com/youtube/v3/search?{urllib.parse.urlencode(params)}"
                
                req = urllib.request.Request(url, headers={"User-Agent": "GrowthOS-LearningCurator/1.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode("utf-8"))

                items = data.get("items", [])
                results: list[SearchResult] = []

                for item in items:
                    id_info = item.get("id", {})
                    video_id = id_info.get("videoId")
                    if not video_id:
                        continue

                    snippet = item.get("snippet", {})
                    title = snippet.get("title", "Untitled Video")
                    description = snippet.get("description", "")
                    channel = snippet.get("channelTitle", "YouTube Creator")
                    published_at = snippet.get("publishedAt")
                    
                    thumbnails = snippet.get("thumbnails", {})
                    thumb_url = (
                        thumbnails.get("high", {}).get("url") or
                        thumbnails.get("medium", {}).get("url") or
                        thumbnails.get("default", {}).get("url") or
                        f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                    )

                    results.append(SearchResult(
                        resource_id=f"yt_{video_id}",
                        title=title,
                        url=f"https://www.youtube.com/watch?v={video_id}",
                        description=description,
                        source="youtube",
                        type="video",
                        thumbnail=thumb_url,
                        channel=channel,
                        duration_minutes=20,  # estimated video duration
                        published_at=published_at,
                        raw_metadata={"video_id": video_id}
                    ))

                return results
            except urllib.error.HTTPError as e:
                logger.warning(f"YouTube Data API HTTP error {e.code}: {e.reason}")
                return []
            except Exception as e:
                logger.error(f"YouTube Data API search failed for query '{query}': {e}")
                return []

        try:
            return await asyncio.to_thread(_fetch_youtube_sync)
        except Exception as e:
            logger.error(f"YouTube provider async execution error: {e}")
            return []


youtube_provider = YouTubeSearchProvider()
