from typing import Any
from app.config.constants import COLLECTION_AGENT_RUNS
from app.database.collections import get_collection, get_mock_collection
from app.utils.helpers import generate_uuid, get_utc_now


class AgentRunRepository:
    """
    Repository for tracking autonomous agent execution telemetry.
    Collection: agent_runs
    Fields:
      - agent_run_id / id: str (run UUID)
      - user_id: str
      - agent_name / agent: str
      - status: str ('running', 'completed', 'failed')
      - execution_mode: str ('REAL', 'MOCK', 'SEED', 'FALLBACK', 'FAILED')
      - started_at: str (ISO)
      - completed_at: str | None (ISO)
      - input_context_summary: dict
      - tools_called: list[str]
      - queries: list[str]
      - provider: str
      - results_retrieved: int
      - results_selected: int
      - decision_summary: str
      - database_writes: list[str]
      - error: str | None
      - metadata: dict
    """

    async def start_run(
        self,
        user_id: str,
        agent_name: str,
        input_context_summary: dict[str, Any] | None = None,
        skills_considered: list[str] | None = None,
        execution_mode: str = "REAL",
        metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        run_id = generate_uuid()
        now = get_utc_now()
        doc = {
            "id": run_id,
            "agent_run_id": run_id,
            "user_id": user_id,
            "agent_name": agent_name,
            "agent": agent_name,
            "status": "running",
            "execution_mode": execution_mode,
            "started_at": now,
            "completed_at": None,
            "input_context_summary": input_context_summary or {},
            "skills_considered": skills_considered or [],
            "tools_called": [],
            "queries": [],
            "provider": "youtube",
            "results_retrieved": 0,
            "results_selected": 0,
            "decision_summary": "",
            "database_writes": [],
            "error": None,
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
        execution_mode: str = "REAL",
        tools_called: list[str] | None = None,
        queries: list[str] | None = None,
        provider: str = "youtube",
        results_retrieved: int = 0,
        results_selected: int = 0,
        decision_summary: str = "",
        database_writes: list[str] | None = None,
        metadata_updates: dict[str, Any] | None = None
    ) -> bool:
        now = get_utc_now()
        updates: dict[str, Any] = {
            "status": status,
            "execution_mode": execution_mode,
            "completed_at": now,
            "provider": provider,
            "results_retrieved": results_retrieved,
            "results_selected": results_selected,
            "decision_summary": decision_summary,
            "database_writes": database_writes or ["recommendations", "agent_runs"],
            "resources_generated": results_selected
        }
        if tools_called is not None:
            updates["tools_called"] = tools_called
        if queries is not None:
            updates["queries"] = queries
        if metadata_updates:
            for k, v in metadata_updates.items():
                updates[f"metadata.{k}"] = v

        col = get_collection(COLLECTION_AGENT_RUNS)
        if col is not None:
            res = await col.update_one({"$or": [{"id": run_id}, {"agent_run_id": run_id}]}, {"$set": updates})
            return res.modified_count > 0
        else:
            mock = get_mock_collection(COLLECTION_AGENT_RUNS)
            for m in mock:
                if m.get("id") == run_id or m.get("agent_run_id") == run_id:
                    m.update(updates)
                    if metadata_updates:
                        m.setdefault("metadata", {}).update(metadata_updates)
                    return True
            return False

    async def fail_run(
        self,
        run_id: str,
        error: str,
        execution_mode: str = "FAILED",
        tools_called: list[str] | None = None,
        queries: list[str] | None = None,
        provider: str = "youtube",
        metadata_updates: dict[str, Any] | None = None
    ) -> bool:
        now = get_utc_now()
        updates: dict[str, Any] = {
            "status": "failed",
            "execution_mode": execution_mode,
            "completed_at": now,
            "provider": provider,
            "error": error,
            "decision_summary": f"Execution failed: {error}",
            "database_writes": ["agent_runs"]
        }
        if tools_called is not None:
            updates["tools_called"] = tools_called
        if queries is not None:
            updates["queries"] = queries
        if metadata_updates:
            for k, v in metadata_updates.items():
                updates[f"metadata.{k}"] = v

        col = get_collection(COLLECTION_AGENT_RUNS)
        if col is not None:
            res = await col.update_one({"$or": [{"id": run_id}, {"agent_run_id": run_id}]}, {"$set": updates})
            return res.modified_count > 0
        else:
            mock = get_mock_collection(COLLECTION_AGENT_RUNS)
            for m in mock:
                if m.get("id") == run_id or m.get("agent_run_id") == run_id:
                    m.update(updates)
                    if metadata_updates:
                        m.setdefault("metadata", {}).update(metadata_updates)
                    return True
            return False

    async def get_run_by_id(self, run_id: str) -> dict[str, Any] | None:
        """Fetch a specific agent execution record by agent_run_id or id."""
        col = get_collection(COLLECTION_AGENT_RUNS)
        if col is not None:
            doc = await col.find_one({"$or": [{"agent_run_id": run_id}, {"id": run_id}]})
            if doc:
                doc.pop("_id", None)
                # Ensure alias fields exist
                doc.setdefault("agent_run_id", doc.get("id"))
                doc.setdefault("agent", doc.get("agent_name"))
            return doc
        else:
            mock = get_mock_collection(COLLECTION_AGENT_RUNS)
            for m in mock:
                if m.get("agent_run_id") == run_id or m.get("id") == run_id:
                    clean = dict(m)
                    clean.pop("_id", None)
                    clean.setdefault("agent_run_id", clean.get("id"))
                    clean.setdefault("agent", clean.get("agent_name"))
                    return clean
            return None

    async def get_latest_run(self, user_id: str, agent_name: str) -> dict[str, Any] | None:
        """Get the most recent run for a specific user and agent."""
        col = get_collection(COLLECTION_AGENT_RUNS)
        if col is not None:
            doc = await col.find_one({"user_id": user_id, "$or": [{"agent_name": agent_name}, {"agent": agent_name}]}, sort=[("started_at", -1)])
            if doc:
                doc.pop("_id", None)
                doc.setdefault("agent_run_id", doc.get("id"))
                doc.setdefault("agent", doc.get("agent_name"))
            return doc
        else:
            mock = get_mock_collection(COLLECTION_AGENT_RUNS)
            matching = [m for m in mock if m.get("user_id") == user_id and (m.get("agent_name") == agent_name or m.get("agent") == agent_name)]
            if matching:
                clean = dict(matching[-1])
                clean.pop("_id", None)
                clean.setdefault("agent_run_id", clean.get("id"))
                clean.setdefault("agent", clean.get("agent_name"))
                return clean
            return None


agent_run_repository = AgentRunRepository()

