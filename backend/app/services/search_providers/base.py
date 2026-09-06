"""
Search Provider Interfaces & Models — GrowthOS Learning Curator
"""
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field
from app.utils.helpers import get_utc_now


class SearchResult(BaseModel):
    resource_id: str = Field(default="", description="Unique provider ID or hash")
    title: str = Field(default="")
    url: str = Field(default="")
    description: str = Field(default="")
    source: str = Field(default="web", description="youtube | web | documentation | course")
    type: str = Field(default="article", description="video | article | book | course | paper | project")
    thumbnail: str = Field(default="")
    channel: str = Field(default="", description="Channel or site author")
    duration_minutes: int | None = Field(default=None)
    published_at: str | None = Field(default=None)
    raw_metadata: dict[str, Any] = Field(default_factory=dict)


class SearchProvider(ABC):
    """Abstract interface for educational search providers."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 15, filters: dict | None = None) -> list[SearchResult]:
        """Execute query and return clean SearchResult objects."""
        pass
