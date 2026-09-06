"""
Web Search Provider — GrowthOS Learning Curator
Fetches real web articles, official documentation, tutorials, and courses.
Supports Serper API, Tavily, Google Custom Search, and DuckDuckGo fallbacks.
"""
import logging
import urllib.parse
import urllib.request
import json
import asyncio
import re
from typing import Any
from app.config.settings import settings
from app.services.search_providers.base import SearchProvider, SearchResult

logger = logging.getLogger(__name__)


class WebSearchProvider(SearchProvider):
    def __init__(self):
        self.serper_key = settings.SERPER_API_KEY
        self.tavily_key = settings.TAVILY_API_KEY
        self.google_key = settings.GOOGLE_SEARCH_KEY
        self.google_cx = settings.GOOGLE_CX

    async def search(self, query: str, max_results: int = 15, filters: dict | None = None) -> list[SearchResult]:
        def _fetch_sync() -> list[SearchResult]:
            # 1. Try Serper API
            if self.serper_key and not self.serper_key.startswith("your_"):
                res = self._search_serper(query, max_results)
                if res:
                    return res

            # 2. Try Tavily API
            if self.tavily_key and not self.tavily_key.startswith("your_"):
                res = self._search_tavily(query, max_results)
                if res:
                    return res

            # 3. Try Google Custom Search API
            if self.google_key and self.google_cx and not self.google_key.startswith("your_"):
                res = self._search_google_custom(query, max_results)
                if res:
                    return res

            # 4. Fallback DuckDuckGo HTML parser
            return self._search_duckduckgo_fallback(query, max_results)

        try:
            return await asyncio.to_thread(_fetch_sync)
        except Exception as e:
            logger.error(f"WebSearchProvider search failed: {e}")
            return []

    def _search_serper(self, query: str, max_results: int) -> list[SearchResult]:
        try:
            url = "https://google.serper.dev/search"
            payload = json.dumps({"q": query, "num": max_results}).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"X-API-KEY": self.serper_key, "Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            for item in data.get("organic", []):
                link = item.get("link")
                if not link or not link.startswith("http"):
                    continue
                results.append(SearchResult(
                    resource_id=f"web_{hash(link) & 0xffffffff:x}",
                    title=item.get("title", "Educational Resource"),
                    url=link,
                    description=item.get("snippet", ""),
                    source="web",
                    type="article",
                    channel=self._extract_domain(link),
                    duration_minutes=15
                ))
            return results
        except Exception as e:
            logger.warning(f"Serper API search failed: {e}")
            return []

    def _search_tavily(self, query: str, max_results: int) -> list[SearchResult]:
        try:
            url = "https://api.tavily.com/search"
            payload = json.dumps({"api_key": self.tavily_key, "query": query, "max_results": max_results}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            for item in data.get("results", []):
                link = item.get("url")
                if not link or not link.startswith("http"):
                    continue
                results.append(SearchResult(
                    resource_id=f"tav_{hash(link) & 0xffffffff:x}",
                    title=item.get("title", "Educational Resource"),
                    url=link,
                    description=item.get("content", ""),
                    source="web",
                    type="article",
                    channel=self._extract_domain(link),
                    duration_minutes=15
                ))
            return results
        except Exception as e:
            logger.warning(f"Tavily API search failed: {e}")
            return []

    def _search_google_custom(self, query: str, max_results: int) -> list[SearchResult]:
        try:
            params = {
                "key": self.google_key,
                "cx": self.google_cx,
                "q": query,
                "num": min(max_results, 10)
            }
            url = f"https://www.googleapis.com/customsearch/v1?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={"User-Agent": "GrowthOS/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = []
            for item in data.get("items", []):
                link = item.get("link")
                if not link or not link.startswith("http"):
                    continue
                results.append(SearchResult(
                    resource_id=f"goog_{hash(link) & 0xffffffff:x}",
                    title=item.get("title", "Educational Resource"),
                    url=link,
                    description=item.get("snippet", ""),
                    source="web",
                    type="article",
                    channel=self._extract_domain(link),
                    duration_minutes=15
                ))
            return results
        except Exception as e:
            logger.warning(f"Google Custom Search failed: {e}")
            return []

    def _search_duckduckgo_fallback(self, query: str, max_results: int) -> list[SearchResult]:
        try:
            params = {"q": query}
            url = f"https://html.duckduckgo.com/html/?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            with urllib.request.urlopen(req, timeout=6) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            # Extract links using regex
            links = re.findall(r'<a class="result__url" href="([^"]+)">', html)
            titles = re.findall(r'<a class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
            snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)

            results = []
            for i in range(min(len(links), max_results)):
                raw_link = links[i].strip()
                # Unpack DDG redirect link if present
                if "uddg=" in raw_link:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_link).query)
                    link = parsed.get("uddg", [raw_link])[0]
                else:
                    link = raw_link

                if not link.startswith("http"):
                    continue

                raw_title = re.sub(r'<[^>]+>', '', titles[i]).strip() if i < len(titles) else "Educational Article"
                raw_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ""

                results.append(SearchResult(
                    resource_id=f"ddg_{hash(link) & 0xffffffff:x}",
                    title=raw_title or f"Resource on {query}",
                    url=link,
                    description=raw_snippet,
                    source="web",
                    type="article",
                    channel=self._extract_domain(link),
                    duration_minutes=15
                ))

            return results
        except Exception as e:
            logger.warning(f"DuckDuckGo fallback search failed: {e}")
            return []

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            return domain or "Web Source"
        except Exception:
            return "Web Source"


web_provider = WebSearchProvider()
