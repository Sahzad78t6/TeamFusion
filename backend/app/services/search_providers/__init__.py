"""
Search Providers Package — GrowthOS
"""
from app.services.search_providers.base import SearchProvider, SearchResult
from app.services.search_providers.youtube_provider import youtube_provider, YouTubeSearchProvider
from app.services.search_providers.web_provider import web_provider, WebSearchProvider

__all__ = [
    "SearchProvider",
    "SearchResult",
    "youtube_provider",
    "YouTubeSearchProvider",
    "web_provider",
    "WebSearchProvider"
]
