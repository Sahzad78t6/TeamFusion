"""Utility functions for Opportunity Agent."""


def filter_opportunities_by_type(opportunities: list[dict], opp_type: str) -> list[dict]:
    """Filter opportunities by type."""
    return [o for o in opportunities if o.get("type", "").lower() == opp_type.lower()]
