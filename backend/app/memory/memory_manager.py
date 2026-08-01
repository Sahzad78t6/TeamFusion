import logging
from app.config.settings import settings
from app.memory.store import add_memory
from app.memory.retrieve import search_memories
from app.memory.update import update_memory_entry

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
        self.api_key = settings.MEM0_API_KEY

    def save_user_fact(self, user_id: str, fact: str, metadata: dict | None = None):
        logger.info(f"Saving user memory fact for {user_id}: {fact}")
        return add_memory(user_id, fact, metadata)

    def get_user_facts(self, user_id: str, query: str = "") -> list[dict]:
        return search_memories(user_id, query)

    def update_fact(self, user_id: str, old_keyword: str, new_fact: str) -> bool:
        return update_memory_entry(user_id, old_keyword, new_fact)

memory_manager = MemoryManager()
