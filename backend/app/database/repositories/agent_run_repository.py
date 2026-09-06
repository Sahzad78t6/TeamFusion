from typing import Any
from app.config.constants import COLLECTION_AGENT_RUNS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now

class AgentRunRepository:
    """
    Repository for tracking autonomous agent execution telemetry.
    Collection: agent_runs
    Fields:
      - id: str (run_id)
      - user_id: str
      - agent_name: str
      - status: str ('running', 'completed', 'failed')
      - started_at: str (ISO)
      - completed_at: str | None (ISO)
      - skills_considered: list[str]
      - resources_generated: int
      - metadata: dict
    """

    async def start_run(
        self,
        user_id: str,
        agent_name: str,
        skills_considered: list[str] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        run_id = generate_uuid()
        now = get_utc_now()
        doc = {
            "id": run_id,
            "user_id": user_id,
            "agent_name": agent_name,
            "status": "running",
            "started_at": now,
            "completed_at": None,
            "skills_considered": skills_considered or [],
            "resources_generated": 0,
            "metadata": metadata or {}
        }

        col = get_collection(COLLECTION_AGENT_RUNS)
        if col is not None:
            await col.insert_one(doc)
            doc.pop("_id", None)
        else:
            mock = get_mock_collection(COLLECTION_AGENT_RUNS)
            clean_doc = dict(doc)
            clean_doc.pop("_id", None)
            mock.append(clean_doc)

        return doc

    async def complete_run(
        self,
        run_id: str,
        status: str = "completed",
        resources_generated: int = 0,
        metadata_updates: dict[str, Any] | None = None
    ) -> bool:
        now = get_utc_now()
        updates: dict[str, Any] = {
            "status": status,
            "completed_at": now,
            "resources_generated": resources_generated
        }
        if metadata_updates:
            for k, v in metadata_updates.items():
                updates[f"metadata.{k}"] = v

        col = get_collection(COLLECTION_AGENT_RUNS)
        if col is not None:
            res = await col.update_one({"id": run_id}, {"$set": updates})
            return res.modified_count > 0
        else:
            mock = get_mock_collection(COLLECTION_AGENT_RUNS)
            for m in mock:
                if m.get("id") == run_id:
                    m["status"] = status
                    m["completed_at"] = now
                    m["resources_generated"] = resources_generated
                    if metadata_updates:
                        m.setdefault("metadata", {}).update(metadata_updates)
                    return True
            return False

    async def get_latest_run(self, user_id: str, agent_name: str) -> dict[str, Any] | None:
        """Get the most recent run for a specific user and agent."""
        col = get_collection(COLLECTION_AGENT_RUNS)
        if col is not None:
            doc = await col.find_one({"user_id": user_id, "agent_name": agent_name}, sort=[("started_at", -1)])
            if doc:
                doc.pop("_id", None)
            return doc
        else:
            mock = get_mock_collection(COLLECTION_AGENT_RUNS)
            matching = [m for m in mock if m.get("user_id") == user_id and m.get("agent_name") == agent_name]
            if matching:
                clean = dict(matching[-1])
                clean.pop("_id", None)
                return clean
            return None


agent_run_repository = AgentRunRepository()
