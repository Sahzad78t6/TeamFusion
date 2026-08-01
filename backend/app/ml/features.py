"""
Feature extraction utilities for the ML models.
Transforms raw data into feature vectors suitable for scikit-learn or other ML inference.
"""

def extract_growth_features(tasks_completed: int, total_hours: float, streak_days: int) -> list[float]:
    """Convert raw growth inputs into a normalized feature array."""
    # Example normalization for a simple model
    return [
        float(tasks_completed) / 100.0,
        total_hours / 40.0,
        float(streak_days) / 30.0
    ]

def extract_burnout_features(mood_score: int, energy_level: int, total_hours: float) -> list[float]:
    """Convert raw burnout inputs into a feature array."""
    return [
        float(mood_score) / 5.0,
        float(energy_level) / 5.0,
        total_hours / 60.0
    ]
