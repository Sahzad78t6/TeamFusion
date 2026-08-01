import logging
import json
import re
from groq import Groq
from app.config.settings import settings
from app.exceptions import LLMUnavailableError, LLMJSONParseError

logger = logging.getLogger(__name__)

class GroqClientWrapper:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = settings.GROQ_MODEL or "llama-3.3-70b-versatile"
        self._client = None
        self.last_degraded = False
        self.last_degraded_reason = None

    @property
    def client(self):
        if self._client is None and self.api_key and self.api_key not in ("mock_groq_api_key", "YOUR_GROQ_API_KEY"):
            try:
                self._client = Groq(api_key=self.api_key, timeout=15.0)
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        return self._client

    def generate(self, prompt: str, system_instruction: str = "", raise_on_error: bool = False) -> str:
        logger.info(f"Generating Groq output for prompt: '{prompt[:60]}...'")
        self.last_degraded = False
        self.last_degraded_reason = None

        if not self.api_key or self.api_key in ("mock_groq_api_key", "YOUR_GROQ_API_KEY"):
            logger.error("GROQ_API_KEY is unconfigured or set to default mock key.")
            self.last_degraded = True
            self.last_degraded_reason = "llm_unconfigured"
            if raise_on_error:
                raise LLMUnavailableError("Groq API key is unconfigured or set to mock default key.")
            return f"GrowthOS AI Strategy: Focused growth roadmap aligned with your target goals ({prompt[:40]})."

        sys_inst = system_instruction or "You are GrowthOS AI, an expert AI career architect."

        client = self.client
        if client:
            try:
                messages = []
                if sys_inst:
                    messages.append({"role": "system", "content": sys_inst})
                messages.append({"role": "user", "content": prompt})

                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=self.model_name,
                    temperature=0.7,
                    max_tokens=1024,
                    timeout=15.0,
                )
                if chat_completion.choices and chat_completion.choices[0].message.content:
                    return chat_completion.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"Groq API execution failed ({e}).", exc_info=True)
                self.last_degraded = True
                self.last_degraded_reason = "llm_api_error"
                if raise_on_error:
                    raise LLMUnavailableError(f"Groq API request failed: {e}")

        if not self.last_degraded:
            self.last_degraded = True
            self.last_degraded_reason = "llm_unavailable"

        if raise_on_error:
            raise LLMUnavailableError("Groq API is unavailable or client initialization failed.")

        return f"GrowthOS AI Strategy: Focused growth roadmap aligned with your target goals ({prompt[:40]})."

    def generate_json(self, prompt: str, system_instruction: str = "", raise_on_error: bool = False) -> dict | list | None:
        raw_text = self.generate(
            prompt=prompt + "\nIMPORTANT: Return ONLY valid JSON output without markdown backticks or commentary.",
            system_instruction=system_instruction,
            raise_on_error=raise_on_error
        )
        if self.last_degraded and not raise_on_error:
            return None

        try:
            cleaned = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', raw_text).strip()
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Failed to parse JSON from Groq response ({e}). Raw text: {raw_text[:100]}")
            self.last_degraded = True
            self.last_degraded_reason = "json_parse_failed"
            if raise_on_error:
                raise LLMJSONParseError(f"Groq LLM returned invalid JSON output: {e}. Raw response: {raw_text[:200]}")
            return None


groq_llm = GroqClientWrapper()
