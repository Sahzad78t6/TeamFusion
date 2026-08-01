from app.agents.supervisor.agent import supervisor_agent
from app.graph.graph import run_growthos_graph

def test_supervisor_agent():
    res = supervisor_agent.run("user_123", "I want to create a daily plan")
    assert res["next_step"] == "planner"

def test_langgraph_execution():
    res = run_growthos_graph("user_123", "Curate python courses for me")
    assert res["user_id"] == "user_123"
    assert len(res["executed_nodes"]) > 0
