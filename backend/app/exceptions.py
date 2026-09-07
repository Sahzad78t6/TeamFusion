"""GrowthOS custom exceptions for structured error handling."""


class GrowthOSError(Exception):
    """Base exception for GrowthOS errors."""
    pass


class LLMUnavailableError(GrowthOSError):
    """Raised when LLM API (OpenAI) is unconfigured, unreachable, or encounters an API error."""
    pass


class LLMJSONParseError(GrowthOSError):
    """Raised when LLM API returns invalid or garbled JSON that cannot be parsed."""
    pass


class AgentValidationError(GrowthOSError):
    """Raised when agent input or output fails Pydantic validation."""
    pass


class DatabaseError(GrowthOSError):
    """Raised when a database operation fails."""
    pass


class MemoryError(GrowthOSError):
    """Raised when Mem0 memory operations fail."""
    pass


class YouTubeError(GrowthOSError):
    """Base exception for YouTube Data API errors."""
    pass


class YouTubeApiKeyMissingError(YouTubeError):
    """Raised when YouTube API key is missing or unconfigured."""
    pass


class YouTubeQuotaExceededError(YouTubeError):
    """Raised when YouTube Data API returns 429 / RESOURCE_EXHAUSTED."""
    pass


class YouTubeUnavailableError(YouTubeError):
    """Raised when YouTube Data API cannot be reached or returns an unexpected error."""
    pass
