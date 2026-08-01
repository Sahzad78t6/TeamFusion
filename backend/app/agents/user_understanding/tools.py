def extract_skills_from_profile(profile_text: str) -> list[str]:
    keywords = ["Python", "FastAPI", "React", "TypeScript", "AI", "Machine Learning", "MongoDB", "SQL", "Docker"]
    found = [kw for kw in keywords if kw.lower() in profile_text.lower()]
    return found or ["General Software Engineering"]
