"""
Agent Execution Observability Router — GrowthOS
Exposes development & telemetry endpoints to verify real agent execution records.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.auth import get_current_user_id
from app.database.repositories.agent_run_repository import agent_run_repository

router = APIRouter(prefix="/agents", tags=["Agent Observability"])


@router.get("/runs/{agent_run_id}")
async def get_agent_run(
    agent_run_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Fetch complete execution telemetry for a specific agent run.
    Verifies authentic execution mode (REAL vs FAILED), queries, tools called, and decisions.
    """
    run = await agent_run_repository.get_run_by_id(agent_run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AgentRun '{agent_run_id}' not found."
        )

    # Scoped access: verify ownership unless platform admin
    if run.get("user_id") and run.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot view execution records of another user."
        )

    first_query = run.get("queries", [""])[0] if run.get("queries") else ""
    return {
        "agent": run.get("agent_name") or run.get("agent", "learning_curator"),
        "agent_run_id": run.get("agent_run_id") or run.get("id"),
        "user_id": run.get("user_id"),
        "execution_mode": run.get("execution_mode", "REAL"),
        "status": run.get("status", "completed"),
        "started_at": run.get("started_at"),
        "completed_at": run.get("completed_at"),
        "context_used": run.get("input_context_summary", {}),
        "tools_called": run.get("tools_called", []),
        "provider": run.get("provider", "youtube"),
        "query": first_query,
        "queries": run.get("queries", []),
        "results_retrieved": run.get("results_retrieved", 0),
        "results_selected": run.get("results_selected", 0),
        "database_writes": run.get("database_writes", ["recommendations", "agent_runs"]),
        "decision_summary": run.get("decision_summary", ""),
        "error": run.get("error"),
        "errors": [run["error"]] if run.get("error") else []
    }


@router.get("/runs/latest/{agent_name}")
async def get_latest_agent_run(
    agent_name: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Fetch the most recent execution record for this user and agent.
    Used by frontend observability panels to display live agent status.
    """
    run = await agent_run_repository.get_latest_run(user_id=user_id, agent_name=agent_name)
    if not run:
        return {
            "agent": agent_name,
            "agent_run_id": None,
            "user_id": user_id,
            "execution_mode": "NEVER_RUN",
            "status": "idle",
            "provider": "youtube",
            "query": "",
            "queries": [],
            "results_retrieved": 0,
            "results_selected": 0,
            "database_writes": [],
            "decision_summary": "No runs recorded yet for this user.",
            "error": None
        }

    first_query = run.get("queries", [""])[0] if run.get("queries") else ""
    return {
        "agent": run.get("agent_name") or run.get("agent", agent_name),
        "agent_run_id": run.get("agent_run_id") or run.get("id"),
        "user_id": run.get("user_id"),
        "execution_mode": run.get("execution_mode", "REAL"),
        "status": run.get("status", "completed"),
        "started_at": run.get("started_at"),
        "completed_at": run.get("completed_at"),
        "context_used": run.get("input_context_summary", {}),
        "tools_called": run.get("tools_called", []),
        "provider": run.get("provider", "youtube"),
        "query": first_query,
        "queries": run.get("queries", []),
        "results_retrieved": run.get("results_retrieved", 0),
        "results_selected": run.get("results_selected", 0),
        "database_writes": run.get("database_writes", ["recommendations", "agent_runs"]),
        "decision_summary": run.get("decision_summary", ""),
        "error": run.get("error"),
        "errors": [run["error"]] if run.get("error") else []
    }
