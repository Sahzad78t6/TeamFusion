import asyncio
from unittest.mock import patch
from pydantic import ValidationError
from app.agents.opportunity.agent import opportunity_agent
from app.agents.opportunity.schemas import OpportunityInput
from app.agents.opportunity.tools import find_matched_opportunities

def test_pydantic_validation_invalid_input():
    print("[Testing Opportunity Pydantic Validation on Invalid Input]")
    try:
        OpportunityInput(role="")
        assert False, "Should have raised ValidationError for empty role"
    except ValidationError as e:
        print("[PASS] Pydantic validation rejected invalid input:", e.errors()[0]["msg"])

def test_missing_dataset_exception():
    print("[Testing Opportunity Missing Dataset Exception Handling]")
    with patch("app.agents.opportunity.tools.CSV_PATH", "/non/existent/path/opportunities.csv"):
        try:
            find_matched_opportunities(role="AI Engineer", raise_on_error=True)
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError as e:
            print("[PASS] Missing dataset raised typed exception:", str(e))

def test_mem0_failure_tolerance():
    print("[Testing Opportunity Mem0 Failure Tolerance]")
    with patch("app.memory.memory_manager.add_memory", side_effect=Exception("Mem0 Service Outage")):
        res = opportunity_agent.match("test_opp1", {"target_role": "AI Architect"})
        assert len(res) > 0
        print("[PASS] Agent completed successfully despite Mem0 failure.")

def test_happy_path():
    print("[Testing Opportunity Happy Path]")
    res = opportunity_agent.match("test_opp2", {"target_role": "Senior AI Agent Architect", "skills": ["Python", "FastAPI"]})
    assert len(res) > 0
    top_opp = res[0]
    assert "title" in top_opp
    assert "relevance_score" in top_opp
    print(f"[PASS] Happy path executed successfully. Top match: '{top_opp['title']}' (Score: {top_opp['relevance_score']})")

if __name__ == "__main__":
    test_pydantic_validation_invalid_input()
    test_missing_dataset_exception()
    test_mem0_failure_tolerance()
    test_happy_path()
