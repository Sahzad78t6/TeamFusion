from app.agents.user_understanding.tools import extract_skills_from_profile
from app.llm.gemini import gemini_llm

class UserUnderstandingAgent:
    def analyze(self, user_id: str, profile_text: str) -> dict:
        extracted = extract_skills_from_profile(profile_text)
        summary = gemini_llm.generate(
            prompt=f"Profile text: '{profile_text}'. Extracted skills: {extracted}.",
            system_instruction="Analyze user identity profile."
        )
        return {
            "user_id": user_id,
            "skills": extracted,
            "profile_insight": summary
        }

user_understanding_agent = UserUnderstandingAgent()
