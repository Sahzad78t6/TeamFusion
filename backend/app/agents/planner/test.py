import asyncio
from unittest.mock import patch
from pydantic import ValidationError
from app.agents.planner.agent import planner_agent
from app.agents.planner.tools import generate_ai_roadmap
from app.exceptions import LLMJSONParseError

def test_pydantic_validation_invalid_input():
    print("[Testing Planner Pydantic Validation on Invalid Input]")
    try:
        asyncio.run(planner_agent.create_and_save_plan("test_p1", goals=[]))
        assert False, "Should have raised ValidationError for empty goals list"
    except ValidationError as e:
        print("[PASS] Pydantic validation rejected invalid input:", e.errors()[0]["msg"])

def test_garbled_groq_exception():
    print("[Testing Planner Garbled Groq Exception Handling]")
    with patch("app.llm.groq_client.groq_llm.generate", return_value="INVALID JSON {{"):
        try:
            generate_ai_roadmap(goals=["Master FastAPI"], raise_on_error=True)
            assert False, "Should have raised LLMJSONParseError"
        except LLMJSONParseError as e:
            print("[PASS] Garbled Groq response raised typed exception:", str(e))

def test_mem0_failure_tolerance():
    print("[Testing Planner Mem0 Failure Tolerance]")
    with patch("app.memory.memory_manager.add_memory", side_effect=Exception("Mem0 Timeout")):
        res = asyncio.run(planner_agent.create_and_save_plan("test_p2", ["Learn LangChain"]))
        assert res["user_id"] == "test_p2"
        print("[PASS] Agent completed successfully despite Mem0 failure.")

def test_happy_path():
    print("[Testing Planner Happy Path]")
    res = asyncio.run(planner_agent.create_and_save_plan("test_p3", ["Build AI Swarm"]))
    assert res["user_id"] == "test_p3"
    assert len(res["tasks"]) > 0
    print("[PASS] Happy path executed successfully. Tasks generated:", len(res["tasks"]))

if __name__ == "__main__":
    test_pydantic_validation_invalid_input()
    test_garbled_groq_exception()
    test_mem0_failure_tolerance()
    test_happy_path()
