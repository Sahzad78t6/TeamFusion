"""
In-memory store fallback for Mem0 context retention.
"""
memory_storage: dict[str, list[dict]] = {}

def add_memory(user_id: str, memory_text: str, metadata: dict | None = None) -> dict:
    if user_id not in memory_storage:
        memory_storage[user_id] = []
    entry = {
        "text": memory_text,
        "metadata": metadata or {},
    }
    memory_storage[user_id].append(entry)
    return entry


def get_memories(user_id: str) -> list[dict]:
    return memory_storage.get(user_id, [])
