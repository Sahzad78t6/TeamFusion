import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GeminiWrapper:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-1.5-pro"

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        logger.info(f"Generating LLM output for prompt prefix: {prompt[:40]}...")
        if not self.api_key or self.api_key == "mock_gemini_api_key":
            return f"[AI Response]: Based on your goals, here is an optimized AI suggestion for: '{prompt[:50]}...'"
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name, system_instruction=system_instruction)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.warning(f"Gemini API error ({e}). Returning fallback response.")
            return f"[Fallback Response]: AI processed your request for: '{prompt[:50]}...'"

gemini_llm = GeminiWrapper()
