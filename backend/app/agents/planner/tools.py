from app.utils.helpers import generate_uuid

def generate_daily_tasks(goals: list[str]) -> list[dict]:
    tasks = []
    for idx, g in enumerate(goals):
        tasks.append({
            "id": generate_uuid(),
            "title": f"Work on {g}",
            "completed": False,
            "duration_mins": 45,
            "priority": "high" if idx == 0 else "medium"
        })
    return tasks
