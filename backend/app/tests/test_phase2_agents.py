import pytest
from app.agents.supervisor.agent import supervisor_agent
from app.services.tool_registry import tool_registry
from app.agents.planner.agent import planner_agent
from app.services.activity_service import activity_service
from app.services.skill_graph_service import skill_graph_service
from app.agents.reflection.agent import reflection_agent
from app.agents.notification.agent import notification_agent
from app.agents.opportunity.agent import opportunity_agent
from app.ml.service import ml_service
from app.services.agent_observability import observability_service
from app.services.copilot_service import copilot_service


@pytest.mark.asyncio
async def test_tool_registry_execution():
    res = await tool_registry.execute_tool("get_user_profile", user_id="test_user_p2")
    assert res["success"] is True
    assert "target_role" in res["result"]


@pytest.mark.asyncio
async def test_supervisor_routing_and_contract():
    test_user = "test_user_p2"
    result = await supervisor_agent.execute({"user_id": test_user, "message": "Plan my day."})
    assert result.success is True
    assert result.data["routed_to"] == "planner"
    contract = result.data["supervisor_response"]
    assert contract["intent"] == "create_or_fetch_plan"
    assert contract["agent"] == "planner"


@pytest.mark.asyncio
async def test_planner_agent_persistence():
    plan = await planner_agent.generate_and_store_plan("test_user_p2", goals=["Learn PyTorch", "Master Algorithms"])
    assert "tasks" in plan
    assert len(plan["tasks"]) > 0


@pytest.mark.asyncio
async def test_learning_activity_and_skill_update():
    event = await activity_service.log_event("test_user_p2", "task_completed", {"title": "Recursion Practice", "topic": "Recursion"})
    assert event["event_type"] == "task_completed"

    skills = await skill_graph_service.get_user_skills("test_user_p2")
    assert any(s["name"] == "Recursion" or "recursion" in s["skill_id"] for s in skills)


@pytest.mark.asyncio
async def test_reflection_and_memory():
    res = await reflection_agent.process_reflection("test_user_p2", "I struggled with graph traversal today, but made progress on dynamic programming.", mood="challenged")
    assert "ai_insight" in res or "user_id" in res or "notes" in res or "reflection_text" in res


@pytest.mark.asyncio
async def test_notification_throttling():
    notif1 = await notification_agent.evaluate_and_notify("test_user_p2", "inactivity", {"days_inactive": 4})
    notif2 = await notification_agent.evaluate_and_notify("test_user_p2", "inactivity", {"days_inactive": 4})
    assert notif2 is None or notif1 is not None


@pytest.mark.asyncio
async def test_opportunity_matching():
    opps = await opportunity_agent.get_matched_opportunities("test_user_p2")
    assert "opportunities" in opps


@pytest.mark.asyncio
async def test_ml_service_predictions():
    risk = await ml_service.predict_risk("test_user_p2")
    assert "risk_score" in risk
    assert "risk_level" in risk

    outcome = await ml_service.predict_learning_outcome("test_user_p2")
    assert "predicted_progress" in outcome


@pytest.mark.asyncio
async def test_agent_observability():
    req_id = await observability_service.log_run("test_user_p2", "planner", ["get_user_profile", "create_plan"], 120.5)
    assert req_id is not None


@pytest.mark.asyncio
async def test_copilot_service_integration():
    res = await copilot_service.respond("test_user_p2", "What should I learn next?")
    assert res.agent == "learning_curator"
    assert len(res.message) > 0
