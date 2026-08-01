import logging
import json
import re
import urllib.request
import urllib.parse
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Safely resolve Gemini SDK or HTTP REST fallback
genai = None
sdk_type = None  # "generativeai" | "genai" | None

try:
    import google.generativeai as _genai
    genai = _genai
    sdk_type = "generativeai"
except Exception:
    try:
        from google import genai as _genai
        genai = _genai
        sdk_type = "genai"
    except Exception:
        genai = None
        sdk_type = None


class GeminiWrapper:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash"

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        logger.info(f"Generating Gemini output for prompt: '{prompt[:60]}...'")
        if not self.api_key or self.api_key in ("mock_gemini_api_key", "YOUR_GEMINI_API_KEY"):
            return f"GrowthOS AI Strategy: Focused growth roadmap aligned with your target goals ({prompt[:40]})."

        sys_inst = system_instruction or "You are GrowthOS AI, an expert AI career architect."

        # Strategy 1: google.generativeai SDK
        if sdk_type == "generativeai" and genai is not None:
            try:
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=sys_inst
                )
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"google.generativeai error ({e}). Trying REST endpoint...")

        # Strategy 2: google.genai SDK
        elif sdk_type == "genai" and genai is not None:
            try:
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={"system_instruction": sys_inst}
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"google.genai error ({e}). Trying REST endpoint...")

        # Strategy 3: Direct HTTP REST Call to Google Gemini API (zero-dependency fallback)
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "system_instruction": {"parts": [{"text": sys_inst}]}
            }
            
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                candidates = result.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
        except Exception as e:
            logger.warning(f"Gemini REST API error ({e}). Utilizing AI strategy fallback.")

        return f"GrowthOS AI Strategy: Continuous deep learning focus for '{prompt[:40]}...'"

    def generate_json(self, prompt: str, system_instruction: str = "") -> dict | list | None:
        raw_text = self.generate(
            prompt=prompt + "\nIMPORTANT: Return ONLY valid JSON output without markdown backticks or commentary.",
            system_instruction=system_instruction
        )
        try:
            cleaned = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', raw_text).strip()
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"Failed to parse JSON from Gemini response ({e}).")
            return None

gemini_llm = GeminiWrapper()
