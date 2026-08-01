"""
Backward-compatible LLM client for GrowthOS.
Provides complete_json() used by agent tools.py files.
Delegates to the LLMProvider abstraction (OpenAI backend).
"""
import logging
from app.llm.provider import llm_provider
from app.exceptions import LLMUnavailableError, LLMJSONParseError

logger = logging.getLogger(__name__)


async def complete_json(prompt: str, system: str = "", *, timeout: float | None = None) -> dict | None:
    """
    Generate a JSON response from the LLM.
    Returns parsed dict on success, None on failure (graceful degradation).
    """
    try:
        return llm_provider.generate_json(
            prompt=prompt,
            system_instruction=system or "You are a helpful assistant. Return valid JSON.",
        )
    except (LLMUnavailableError, LLMJSONParseError) as exc:
        logger.warning("LLM JSON completion failed: %s", exc)
        return None
    except Exception as exc:
        logger.warning("LLM JSON completion unexpected error: %s", exc)
        return None
