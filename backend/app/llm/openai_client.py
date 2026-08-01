"""
OpenAI client wrapper for GrowthOS.
Provides generate() and generate_json() methods for all LLM interactions.
"""
import json
import re
import logging
from openai import OpenAI
from app.config.settings import settings
from app.exceptions import LLMUnavailableError, LLMJSONParseError

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Thin wrapper around the OpenAI SDK with JSON extraction support."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL or "gpt-4o-mini"
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI | None:
        if self._client is None and self._is_configured():
            try:
                self._client = OpenAI(api_key=self.api_key, timeout=30.0)
                logger.info("OpenAI client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        return self._client

    def _is_configured(self) -> bool:
        return bool(self.api_key) and self.api_key not in ("YOUR_OPENAI_API_KEY", "")

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        """Generate text completion from OpenAI."""
        logger.info(f"OpenAI generate: prompt='{prompt[:80]}...'")

        if not self._is_configured():
            logger.warning("OpenAI API key is not configured.")
            raise LLMUnavailableError("OpenAI API key is not configured. Set OPENAI_API_KEY in .env")

        client = self.client
        if not client:
            raise LLMUnavailableError("OpenAI client failed to initialize.")

        system = system_instruction or "You are GrowthOS AI, an expert AI career growth architect."

        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )

            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()

            raise LLMUnavailableError("OpenAI returned an empty response.")

        except LLMUnavailableError:
            raise
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}", exc_info=True)
            raise LLMUnavailableError(f"OpenAI API request failed: {e}")

    def generate_json(self, prompt: str, system_instruction: str = "") -> dict | list | None:
        """Generate a JSON response from OpenAI, with automatic extraction and parsing."""
        json_prompt = prompt + "\nIMPORTANT: Return ONLY valid JSON output without markdown backticks or commentary."

        raw_text = self.generate(prompt=json_prompt, system_instruction=system_instruction)

        try:
            cleaned = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', raw_text).strip()
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Failed to parse JSON from OpenAI response: {e}. Raw: {raw_text[:200]}")
            raise LLMJSONParseError(f"OpenAI returned invalid JSON: {e}. Raw response: {raw_text[:200]}")


openai_client = OpenAIClient()
