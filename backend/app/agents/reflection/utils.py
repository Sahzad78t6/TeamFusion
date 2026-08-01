"""Utility functions for Reflection Agent."""


def check_extreme_burnout(risk_level: str, mood_score: int) -> bool:
    """Determine if burnout risk is extremely high requiring urgent notification."""
    return risk_level.lower() == "high" and mood_score <= 2
