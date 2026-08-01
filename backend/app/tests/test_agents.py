from app.agents.supervisor.agent import supervisor_agent

def test_supervisor_agent():
    res = supervisor_agent.run("user_123", "I want to create a daily plan")
    assert res["next_step"] == "planner"
