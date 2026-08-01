def score_opportunity_match(opp_skills: list[str], user_skills: set[str], base_score: float) -> float:
    matched = sum(1 for s in opp_skills if any(u in s or s in u for u in user_skills))
    total = max(len(opp_skills), 1)
    skill_score = matched / total
    return round(min(0.99, max(0.70, base_score * 0.8 + skill_score * 0.2)), 2)
