from app.memory.store import memory_storage

def update_memory_entry(user_id: str, old_keyword: str, new_memory_text: str) -> bool:
    if user_id in memory_storage:
        for entry in memory_storage[user_id]:
            if old_keyword in entry["text"]:
                entry["text"] = new_memory_text
                return True
    return False
