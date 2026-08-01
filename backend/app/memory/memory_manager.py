"""
Memory Manager for GrowthOS
Integrates with Mem0 for long-term vector memory, with local dict fallback.
"""
import logging
from app.config.settings import settings
from app.memory.store import add_memory, get_memories

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
        self.api_key = settings.MEM0_API_KEY
        self.client = None
        
        if self.api_key and self.api_key != "YOUR_MEM0_API_KEY":
            try:
                from mem0 import Memory
                mem0_config = {
                    "llm": {"provider": "openai", "config": {"api_key": settings.OPENAI_API_KEY}},
                    "embedder": {"provider": "openai", "config": {"api_key": settings.OPENAI_API_KEY}},
                }
                self.client = Memory.from_config(mem0_config)
                logger.info("Mem0 client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Mem0 client: {e}")
        else:
            logger.info("Mem0 API key not found. Using local fallback memory store.")

    def save_user_fact(self, user_id: str, fact: str, metadata: dict | None = None) -> bool:
        """Save a long-term fact to memory."""
        logger.info(f"Saving fact for user {user_id}: {fact}")
        
        if self.client:
            try:
                self.client.add(fact, user_id=user_id, metadata=metadata)
                return True
            except Exception as e:
                logger.error(f"Mem0 add failed: {e}. Falling back to local store.")
        
        # Fallback
        add_memory(user_id, fact, metadata)
        return True

    def get_user_context(self, user_id: str, query: str = "") -> list[dict]:
        """Retrieve relevant context for a user."""
        if self.client:
            try:
                if query:
                    results = self.client.search(query, user_id=user_id)
                else:
                    results = self.client.get_all(user_id=user_id)
                
                # Format Mem0 results
                if results:
                    return [{"text": r.get("memory", ""), "metadata": r.get("metadata", {})} for r in results]
                return []
            except Exception as e:
                logger.error(f"Mem0 retrieve failed: {e}. Falling back to local store.")
                
        # Fallback
        return get_memories(user_id)


memory_manager = MemoryManager()
