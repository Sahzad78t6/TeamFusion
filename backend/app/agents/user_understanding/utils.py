def format_skills_list(skills: list[str]) -> str:
    if not skills:
        return "General Software Engineering"
    return ", ".join(skills)

def compute_initial_drift(experience: str) -> float:
    exp_lower = (experience or "").lower()
    if "senior" in exp_lower or "lead" in exp_lower:
        return 8.5
    elif "beginner" in exp_lower or "junior" in exp_lower:
        return 22.0
    return 14.0
