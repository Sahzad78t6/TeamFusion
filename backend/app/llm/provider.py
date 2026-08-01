"""
LLM Provider abstraction for GrowthOS.
All agents must use LLMProvider.generate() — never call OpenAI directly.
"""
import logging
from app.llm.openai_client import openai_client
from app.exceptions import LLMUnavailableError, LLMJSONParseError

logger = logging.getLogger(__name__)


class LLMProvider:
    """
    Unified LLM interface for all GrowthOS agents.
    Delegates to the configured backend (OpenAI).
    """

    def __init__(self):
        self._client = openai_client

    def generate(self, prompt: str, system_instruction: str = "") -> str | None:
        """Generate a text response from the LLM."""
        try:
            return self._client.generate(prompt=prompt, system_instruction=system_instruction)
        except Exception as e:
            logger.warning(f"LLMProvider generation failed: {e}. Falling back.")
            return None

    def generate_json(self, prompt: str, system_instruction: str = "") -> dict | list | None:
        """Generate a structured JSON response from the LLM."""
        try:
            return self._client.generate_json(prompt=prompt, system_instruction=system_instruction)
        except Exception as e:
            logger.warning(f"LLMProvider JSON generation failed: {e}. Falling back.")
            return None

    def is_available(self) -> bool:
        """Check if the LLM backend is configured and reachable."""
        return self._client._is_configured()


llm_provider = LLMProvider()
