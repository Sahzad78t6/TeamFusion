"""Utility functions for User Understanding Agent."""
import re
from typing import Iterable


def format_skills_list(skills: list[str]) -> str:
    """Format a skills list into a readable string."""
    if not skills:
        return "General Software Engineering"
    return ", ".join(skills)


def compute_initial_drift(experience: str) -> float:
    """Compute initial identity drift based on experience level."""
    exp_lower = (experience or "").lower()
    if "senior" in exp_lower or "expert" in exp_lower:
        return 5.0
    elif "mid" in exp_lower or "intermediate" in exp_lower:
        return 12.0
    elif "junior" in exp_lower or "beginner" in exp_lower:
        return 25.0
    return 15.0
