def route_next_agent(user_query: str) -> str:
    query_lower = user_query.lower()
    if "plan" in query_lower or "schedule" in query_lower or "task" in query_lower:
        return "planner"
    elif "learn" in query_lower or "course" in query_lower or "recommend" in query_lower:
        return "learning_curator"
    elif "job" in query_lower or "opportunity" in query_lower or "career" in query_lower:
        return "opportunity"
    elif "reflect" in query_lower or "mood" in query_lower or "journal" in query_lower:
        return "reflection"
    elif "profile" in query_lower or "onboard" in query_lower or "goal" in query_lower:
        return "user_understanding"
    else:
        return "planner"
