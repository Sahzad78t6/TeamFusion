"""
Memory Service — GrowthOS
Alias interface wrapping MemoryManager.
"""
from typing import Any
from app.memory.memory_manager import memory_manager


class MemoryService:
    def add_memory(self, user_id: str, memory_text: str, metadata: dict[str, Any] | None = None) -> bool:
        return memory_manager.save_user_fact(user_id, memory_text, metadata)

    def get_memories(self, user_id: str, query: str = "") -> list[dict[str, Any]]:
        return memory_manager.get_user_context(user_id, query)


memory_service = MemoryService()
