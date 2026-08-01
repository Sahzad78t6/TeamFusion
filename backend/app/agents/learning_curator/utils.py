"""Utility functions for Learning Curator Agent."""


def group_resources_by_type(resources: list[dict]) -> dict:
    """Group learning resources by their type (e.g., video, book)."""
    grouped = {}
    for r in resources:
        rtype = r.get("type", "other").lower()
        if rtype not in grouped:
            grouped[rtype] = []
        grouped[rtype].append(r)
    return grouped
