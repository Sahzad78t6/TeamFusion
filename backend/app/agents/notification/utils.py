"""Utility functions for Notification Agent."""


def count_unread_notifications(notifications: list[dict]) -> int:
    """Count the number of unread notifications."""
    return sum(1 for n in notifications if not n.get("is_read", True))
