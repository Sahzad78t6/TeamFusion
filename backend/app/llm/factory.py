"""
LLM Factory for GrowthOS.
Creates and returns a configured LLMProvider instance.
Allows future provider swapping without changing agent code.
"""
from app.llm.provider import LLMProvider, llm_provider


class LLMFactory:
    """Factory for creating LLM provider instances."""

    @staticmethod
    def create(provider_type: str = "openai") -> LLMProvider:
        """
        Create and return an LLMProvider instance.
        Currently supports 'openai' only.
        Extend this method to add new providers in the future.
        """
        if provider_type == "openai":
            return llm_provider
        raise ValueError(f"Unsupported LLM provider: {provider_type}")


llm_factory = LLMFactory()
