import logging
import json
import re
from groq import Groq
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GroqClientWrapper:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = settings.GROQ_MODEL or "llama-3.3-70b-versatile"
        self._client = None

    @property
    def client(self):
        if self._client is None and self.api_key and self.api_key not in ("mock_groq_api_key", "YOUR_GROQ_API_KEY"):
            try:
                self._client = Groq(api_key=self.api_key, timeout=15.0)
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
        return self._client

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        logger.info(f"Generating Groq output for prompt: '{prompt[:60]}...'")
        if not self.api_key or self.api_key in ("mock_groq_api_key", "YOUR_GROQ_API_KEY"):
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
                logger.warning(f"Groq API call error ({e}). Utilizing AI strategy fallback.")

        return f"GrowthOS AI Strategy: Focused growth roadmap aligned with your target goals ({prompt[:40]})."

    def generate_json(self, prompt: str, system_instruction: str = "") -> dict | list | None:
        raw_text = self.generate(
            prompt=prompt + "\nIMPORTANT: Return ONLY valid JSON output without markdown backticks or commentary.",
            system_instruction=system_instruction
        )
        try:
            cleaned = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', raw_text).strip()
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"Failed to parse JSON from Groq response ({e}).")
            return None


groq_llm = GroqClientWrapper()
