def calculate_total_duration(tasks: list[dict]) -> int:
    return sum(int(t.get("duration_mins", 30)) for t in tasks)

def filter_tasks_by_priority(tasks: list[dict], priority: str) -> list[dict]:
    return [t for t in tasks if t.get("priority", "").lower() == priority.lower()]
