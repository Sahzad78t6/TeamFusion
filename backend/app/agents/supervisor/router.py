def route_next_agent(user_query: str) -> str:
    """Route explicit requests only; general conversation stays with the supervisor."""
    query = user_query.lower().strip()
    if any(phrase in query for phrase in ("want to become", "want to be", "become a", "become an", "aspire to", "my goal is")):
        return "user_understanding"
    if any(word in query for word in ("plan", "schedule", "task", "roadmap", "today's focus", "today focus")):
        return "planner"
    if any(word in query for word in ("learn", "course", "recommend", "resource", "study", "book", "podcast")):
        return "learning_curator"
    if any(word in query for word in ("job", "opportunity", "career", "internship", "hackathon", "role")):
        return "opportunity"
    if any(word in query for word in ("reflect", "mood", "journal", "burnout", "check-in", "checkin", "stress")):
        return "reflection"
    if any(word in query for word in ("profile", "onboard", "goal", "identity", "skill gap")):
        return "user_understanding"
    return "conversation"