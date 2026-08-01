def compute_burnout_risk_indicator(mood_score: int, energy_level: int, study_hours: float = 0.0) -> str:
    combined = (mood_score + energy_level) / 2.0
    if combined < 2.5 or study_hours > 10.0:
        return "HIGH_RISK"
    elif combined < 3.8 or study_hours > 7.0:
        return "MODERATE"
    return "LOW"
