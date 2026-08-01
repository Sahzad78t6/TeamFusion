"""Utility functions for Planner Agent."""


def calculate_total_duration(tasks: list[dict]) -> int:
    """Calculate the total duration of a list of tasks in minutes."""
    return sum(int(t.get("duration_mins", 30)) for t in tasks)


def filter_tasks_by_priority(tasks: list[dict], priority: str) -> list[dict]:
    """Filter tasks by priority."""
    return [t for t in tasks if t.get("priority", "").lower() == priority.lower()]
