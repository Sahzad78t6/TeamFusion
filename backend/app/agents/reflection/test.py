import asyncio
from unittest.mock import patch
from pydantic import ValidationError
from app.agents.reflection.agent import reflection_agent, extract_sentiment_scores
from app.agents.reflection.schemas import ReflectionInput
from app.exceptions import LLMUnavailableError

def test_pydantic_validation_invalid_input():
    print("[Testing Reflection Pydantic Validation on Invalid Input]")
    try:
        ReflectionInput(mood=10) # Out of bounds 1..5
        assert False, "Should have raised ValidationError for mood out of range"
    except ValidationError as e:
        print("[PASS] Pydantic validation rejected invalid input:", e.errors()[0]["msg"])

def test_garbled_groq_exception():
    print("[Testing Reflection Groq Exception Handling]")
    with patch("app.llm.groq_client.groq_llm.generate", side_effect=LLMUnavailableError("Groq API key invalid")):
        try:
            asyncio.run(reflection_agent.process_and_save("test_ref1", {"notes": "Feeling tired"}, raise_on_error=True))
            assert False, "Should have raised LLMUnavailableError"
        except LLMUnavailableError as e:
            print("[PASS] Broken Groq raised typed exception:", str(e))

def test_mem0_failure_tolerance():
    print("[Testing Reflection Mem0 Failure Tolerance]")
    with patch("app.memory.memory_manager.add_memory", side_effect=Exception("Mem0 Service Disconnected")):
        res = asyncio.run(reflection_agent.process_and_save("test_ref2", {"notes": "Productive day"}))
        assert res["user_id"] == "test_ref2"
        print("[PASS] Agent completed successfully despite Mem0 failure.")

def test_negative_reflection_scoring():
    print("[Testing Negative Reflection Scoring]")
    res = asyncio.run(reflection_agent.process_and_save("test_ref3", {"notes": "I feel exhausted and want to quit"}))
    assert res["risk_level"] != "LOW", f"Expected non-LOW risk, got {res['risk_level']}"
    assert res["mood_score"] <= 2
    print(f"[PASS] Negative reflection correctly scored as {res['risk_level']} (mood_score={res['mood_score']})")

if __name__ == "__main__":
    test_pydantic_validation_invalid_input()
    test_garbled_groq_exception()
    test_mem0_failure_tolerance()
    test_negative_reflection_scoring()
