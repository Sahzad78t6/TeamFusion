import asyncio
from unittest.mock import patch
from pydantic import ValidationError
from app.agents.learning_curator.agent import learning_curator_agent
from app.agents.learning_curator.schemas import LearningCuratorInput
from app.agents.learning_curator.tools import generate_ai_recommendations
from app.exceptions import LLMJSONParseError

def test_pydantic_validation_invalid_input():
    print("[Testing Learning Curator Pydantic Validation on Invalid Input]")
    try:
        LearningCuratorInput(target_role="")
        assert False, "Should have raised ValidationError for empty target_role"
    except ValidationError as e:
        print("[PASS] Pydantic validation rejected invalid input:", e.errors()[0]["msg"])

def test_garbled_groq_exception():
    print("[Testing Learning Curator Garbled Groq Exception Handling]")
    with patch("app.llm.groq_client.groq_llm.generate", return_value="GARBLED DATA {"):
        try:
            generate_ai_recommendations(target_role="AI Architect", raise_on_error=True)
            assert False, "Should have raised LLMJSONParseError"
        except LLMJSONParseError as e:
            print("[PASS] Garbled Groq response raised typed exception:", str(e))

def test_mem0_failure_tolerance():
    print("[Testing Learning Curator Mem0 Failure Tolerance]")
    with patch("app.memory.memory_manager.add_memory", side_effect=Exception("Mem0 Timeout")):
        res = asyncio.run(learning_curator_agent.curate_and_save("test_lc1"))
        assert res["user_id"] == "test_lc1"
        assert len(res["recommendations"]) > 0
        print("[PASS] Agent completed successfully despite Mem0 failure.")

def test_happy_path():
    print("[Testing Learning Curator Happy Path]")
    res = asyncio.run(learning_curator_agent.curate_and_save("test_lc2"))
    assert res["user_id"] == "test_lc2"
    assert len(res["recommendations"]) > 0
    print("[PASS] Happy path executed successfully. Recommendations count:", len(res["recommendations"]))

if __name__ == "__main__":
    test_pydantic_validation_invalid_input()
    test_garbled_groq_exception()
    test_mem0_failure_tolerance()
    test_happy_path()
