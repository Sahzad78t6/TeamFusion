"""
Context Engine Service — GrowthOS
Central coordination service that synthesizes authentic MongoDB states into typed UserContext.
"""
import logging
from typing import Any

from app.context_engine.context_models import UserContext
from app.context_engine.user_state_retriever import user_state_retriever
from app.context_engine.context_builder import context_builder

logger = logging.getLogger(__name__)


class ContextEngineService:
    """
    Main entrypoint for accessing complete, authenticated user context.
    Strictly isolated per user_id. Zero vector DB or mock dependency.
    """

    async def get_user_context(
        self,
        user_id: str,
        topic: str = "",
        target_role: str = ""
    ) -> UserContext:
        """
        Retrieves real MongoDB state and returns normalized UserContext.
        """
        raw_state = await user_state_retriever.retrieve_raw_user_state(user_id)
        context = context_builder.build_context(
            user_id=user_id,
            raw_state=raw_state,
            override_topic=topic,
            override_role=target_role
        )
        logger.info(
            f"[ContextEngine] Built context user={user_id} role='{context.target_role}' "
            f"primary_gap='{context.primary_gap}' hash={context.context_hash}"
        )
        return context


context_engine_service = ContextEngineService()
