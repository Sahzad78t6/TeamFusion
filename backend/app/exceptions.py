class GrowthOSError(Exception):
    """Base exception for GrowthOS errors."""
    pass

class LLMUnavailableError(GrowthOSError):
    """Raised when LLM API (Groq) is unconfigured, unreachable, or encounters an API error."""
    pass

class LLMJSONParseError(GrowthOSError):
    """Raised when LLM API returns invalid or garbled JSON that cannot be parsed into expected schema."""
    pass

class AgentValidationError(GrowthOSError):
    """Raised when agent input or output fails Pydantic validation."""
    pass
