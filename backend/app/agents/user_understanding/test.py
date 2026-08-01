import asyncio
from unittest.mock import patch
from pydantic import ValidationError
from app.agents.user_understanding.agent import user_understanding_agent
from app.agents.user_understanding.tools import generate_identity_twin_analysis
from app.exceptions import LLMJSONParseError, LLMUnavailableError

def test_pydantic_validation_invalid_input():
    print("[Testing Pydantic Validation on Invalid Input]")
    try:
        asyncio.run(user_understanding_agent.analyze_and_save("test_u1", {"goal": ""}))
        assert False, "Should have raised ValidationError for empty goal"
    except ValidationError as e:
        print("[PASS] Pydantic validation rejected invalid input:", e.errors()[0]["msg"])

def test_garbled_groq_exception():
    print("[Testing Garbled Groq Exception Handling]")
    with patch("app.llm.groq_client.groq_llm.generate", return_value="GARBLED NOT JSON {{[["):
        try:
            generate_identity_twin_analysis({"goal": "AI Engineer"}, raise_on_error=True)
            assert False, "Should have raised LLMJSONParseError"
        except LLMJSONParseError as e:
            print("[PASS] Garbled Groq response raised typed exception:", str(e))

def test_mem0_failure_tolerance():
    print("[Testing Mem0 Failure Tolerance]")
    with patch("app.memory.memory_manager.add_memory", side_effect=Exception("Mem0 Cloud Connection Timeout")):
        res = asyncio.run(user_understanding_agent.analyze_and_save("test_u2", {
            "goal": "Principal Architect",
            "skills": ["Python", "FastAPI"]
        }))
        assert res["user_id"] == "test_u2"
        print("[PASS] Agent completed successfully despite Mem0 failure.")

def test_happy_path():
    print("[Testing Happy Path]")
    res = asyncio.run(user_understanding_agent.analyze_and_save("test_u3", {
        "goal": "Senior AI Agent Architect",
        "skills": ["Python", "FastAPI", "React"]
    }))
    assert res["user_id"] == "test_u3"
    assert "identity_score" in res
    print("[PASS] Happy path executed successfully. Score:", res["identity_score"])

if __name__ == "__main__":
    test_pydantic_validation_invalid_input()
    test_garbled_groq_exception()
    test_mem0_failure_tolerance()
    test_happy_path()
