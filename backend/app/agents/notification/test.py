import asyncio
from unittest.mock import patch
from pydantic import ValidationError
from app.agents.notification.agent import notification_agent
from app.agents.notification.schemas import NotificationInput
from app.agents.notification.tools import generate_proactive_notifications
from app.exceptions import LLMJSONParseError

def test_pydantic_validation_invalid_input():
    print("[Testing Notification Pydantic Validation on Invalid Input]")
    try:
        NotificationInput(user_id="", streak=-5)
        assert False, "Should have raised ValidationError for invalid streak"
    except ValidationError as e:
        print("[PASS] Pydantic validation rejected invalid input:", e.errors()[0]["msg"])

def test_garbled_groq_exception():
    print("[Testing Notification Garbled Groq Exception Handling]")
    with patch("app.llm.groq_client.groq_llm.generate", return_value="GARBLED NOT ARRAY {{"):
        try:
            generate_proactive_notifications(user_id="test_n1", raise_on_error=True)
            assert False, "Should have raised LLMJSONParseError"
        except LLMJSONParseError as e:
            print("[PASS] Garbled Groq response raised typed exception:", str(e))

def test_mem0_failure_tolerance():
    print("[Testing Notification Mem0 Failure Tolerance]")
    with patch("app.memory.memory_manager.add_memory", side_effect=Exception("Mem0 Outage")):
        res = asyncio.run(notification_agent.get_and_sync_notifications("test_n2"))
        assert len(res) > 0
        print("[PASS] Agent completed successfully despite Mem0 failure.")

def test_happy_path():
    print("[Testing Notification Happy Path]")
    res = asyncio.run(notification_agent.get_and_sync_notifications("test_n3"))
    assert len(res) > 0
    print("[PASS] Happy path executed successfully. Notifications count:", len(res))

if __name__ == "__main__":
    test_pydantic_validation_invalid_input()
    test_garbled_groq_exception()
    test_mem0_failure_tolerance()
    test_happy_path()
