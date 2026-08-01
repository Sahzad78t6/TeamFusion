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
        try:
            logger.info(f"Saving user memory fact for {user_id}: {fact}")
            return add_memory(user_id, fact, metadata)
        except Exception as e:
            logger.warning(f"Mem0 save_user_fact warning (non-blocking failure): {e}")
            return {"text": fact, "metadata": metadata or {}, "status": "memory_error"}

    def get_user_facts(self, user_id: str, query: str = "") -> list[dict]:
        try:
            return search_memories(user_id, query)
        except Exception as e:
            logger.warning(f"Mem0 get_user_facts warning (non-blocking failure): {e}")
            return []

    def update_fact(self, user_id: str, old_keyword: str, new_fact: str) -> bool:
        try:
            return update_memory_entry(user_id, old_keyword, new_fact)
        except Exception as e:
            logger.warning(f"Mem0 update_fact warning (non-blocking failure): {e}")
            return False

memory_manager = MemoryManager()
