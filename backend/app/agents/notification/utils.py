def count_unread_notifications(notifications: list[dict]) -> int:
    return sum(1 for n in notifications if not n.get("read"))
