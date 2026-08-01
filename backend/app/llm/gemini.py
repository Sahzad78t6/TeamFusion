import logging
import json
import re
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GeminiWrapper:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash"

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        logger.info(f"Generating Gemini output for prompt: '{prompt[:60]}...'")
        if not self.api_key or self.api_key in ("mock_gemini_api_key", "YOUR_GEMINI_API_KEY"):
            return f"GrowthOS AI Strategy: Focused growth roadmap aligned with your target goals ({prompt[:40]})."

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name, system_instruction=system_instruction or "You are GrowthOS AI, an expert AI career architect.")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini API execution error: {e}. Utilizing AI fallback pipeline.")
            return f"GrowthOS AI Insight: Continue building deep domain expertise for: {prompt[:40]}..."

    def generate_json(self, prompt: str, system_instruction: str = "") -> dict | list | None:
        raw_text = self.generate(
            prompt=prompt + "\nIMPORTANT: Return ONLY valid JSON output without markdown backticks or commentary.",
            system_instruction=system_instruction
        )
        try:
            # Clean markdown JSON block formatting if present
            cleaned = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', raw_text).strip()
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"Failed to parse JSON from Gemini response ({e}). Raw response: {raw_text[:100]}")
            return None

gemini_llm = GeminiWrapper()
