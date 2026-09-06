"""
Learning Activity Service — GrowthOS
Centralized event-stream system logging learner interactions and triggering autonomous downstream flows.
"""
import logging
from typing import Any
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import get_utc_now
from app.services.skill_graph_service import skill_graph_service

logger = logging.getLogger(__name__)


class LearningActivityService:
    def __init__(self):
        self.collection_name = "learning_events"

    async def log_event(
        self,
        user_id: str,
        event_type: str,
        metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Record a learning event and trigger autonomous downstream agent workflows."""
        metadata = metadata or {}
        timestamp = get_utc_now()

        event_doc = {
            "user_id": user_id,
            "event_type": event_type,
            "timestamp": timestamp,
            "metadata": metadata
        }

        col = get_collection(self.collection_name)
        if col is not None:
            try:
                await col.insert_one(event_doc)
            except Exception as e:
                logger.error(f"Failed to persist learning event: {e}")
        else:
            get_mock_collection(self.collection_name).append(event_doc)

        logger.info(f"[LearningEvent] user={user_id} type={event_type} meta={metadata}")

        await self._handle_event_triggers(user_id, event_type, metadata)
        return event_doc

    async def _handle_event_triggers(self, user_id: str, event_type: str, metadata: dict[str, Any]):
        """Internal event bus dispatching tasks to downstream services/agents."""
        try:
            if event_type == "task_completed":
                topic = metadata.get("topic") or metadata.get("title", "general")
                await skill_graph_service.update_skill_mastery(
                    user_id=user_id,
                    skill_name=topic,
                    delta_mastery=0.08,
                    evidence=f"Completed task: {metadata.get('title', 'Learning Task')}"
                )

                from app.agents.notification.agent import notification_agent
                await notification_agent.evaluate_and_notify(
                    user_id=user_id,
                    event_type="task_completed",
                    metadata=metadata
                )

            elif event_type == "reflection_submitted":
                from app.agents.notification.agent import notification_agent
                await notification_agent.evaluate_and_notify(
                    user_id=user_id,
                    event_type="reflection_submitted",
                    metadata=metadata
                )

        except Exception as e:
            logger.error(f"Error handling downstream trigger for {event_type}: {e}", exc_info=True)

    async def get_user_activity(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve recent activity stream for user."""
        col = get_collection(self.collection_name)
        if col is not None:
            cursor = col.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
            events = await cursor.to_list(length=limit)
            for ev in events:
                ev["_id"] = str(ev.get("_id", ""))
            return events
        else:
            mock = get_mock_collection(self.collection_name)
            return [m for m in mock if m.get("user_id") == user_id][:limit]

    async def get_days_since_last_activity(self, user_id: str) -> float:
        """Returns days since last user activity for inactivity risk calculation."""
        col = get_collection(self.collection_name)
        latest = None
        if col is not None:
            latest = await col.find_one({"user_id": user_id}, sort=[("timestamp", -1)])
        else:
            mock = get_mock_collection(self.collection_name)
            user_events = [m for m in mock if m.get("user_id") == user_id]
            if user_events:
                latest = user_events[-1]

        if not latest or "timestamp" not in latest:
            return 0.0

        try:
            from datetime import datetime, timezone
            ts_str = latest["timestamp"]
            ts_dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            now_dt = datetime.now(timezone.utc)
            delta = now_dt - ts_dt
            return max(0.0, delta.total_seconds() / 86400.0)
        except Exception:
            return 0.0


activity_service = LearningActivityService()

