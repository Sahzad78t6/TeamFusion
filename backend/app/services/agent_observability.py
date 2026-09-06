"""
Agent Observability Service — GrowthOS
Logs internal agent execution runs for auditing, debugging, and hackathon evaluation.
"""
import logging
import uuid
import time
from typing import Any
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import get_utc_now
from app.schemas.models import AgentRunLog

logger = logging.getLogger(__name__)


class AgentObservabilityService:
    def __init__(self):
        self.collection_name = "agent_runs"

    async def log_run(
        self,
        user_id: str,
        selected_agent: str,
        tool_calls: list[str],
        duration_ms: float,
        success: bool = True,
        error: str | None = None,
        supervisor: str = "supervisor",
    ) -> str:
        request_id = str(uuid.uuid4())
        run_data = AgentRunLog(
            request_id=request_id,
            user_id=user_id,
            supervisor=supervisor,
            selected_agent=selected_agent,
            tool_calls=tool_calls,
            duration_ms=round(duration_ms, 2),
            success=success,
            error=error,
            timestamp=get_utc_now(),
        ).model_dump()

        logger.info(
            f"[AgentRun] req={request_id} user={user_id} agent={selected_agent} "
            f"tools={tool_calls} duration={duration_ms:.2f}ms success={success}"
        )

        try:
            col = get_collection(self.collection_name)
            if col is not None:
                await col.insert_one(run_data)
            else:
                get_mock_collection(self.collection_name).append(run_data)
        except Exception as e:
            logger.warning(f"Failed to persist agent run log to MongoDB: {e}")

        return request_id



observability_service = AgentObservabilityService()
