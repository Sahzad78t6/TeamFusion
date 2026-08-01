"""Utility functions for Supervisor Agent."""


def is_explicit_routing_command(message: str) -> bool:
    """Check if the user explicitly requested routing (e.g., /plan)."""
    return message.strip().startswith("/")
