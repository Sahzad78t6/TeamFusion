from app.memory.store import memory_storage

def search_memories(user_id: str, query: str, top_k: int = 5) -> list[dict]:
    memories = memory_storage.get(user_id, [])
    # Return matched or recent memories
    return memories[-top_k:]
