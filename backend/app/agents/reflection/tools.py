def compute_burnout_risk_indicator(mood_score: int, energy_level: int) -> str:
    combined = (mood_score + energy_level) / 2.0
    if combined < 2.5:
        return "HIGH_RISK"
    elif combined < 3.8:
        return "MODERATE"
    return "LOW"
