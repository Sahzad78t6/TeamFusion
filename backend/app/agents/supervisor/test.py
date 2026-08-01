"""Test script for Supervisor Agent."""
import asyncio
from app.agents.supervisor.agent import supervisor_agent


async def run_test():
    print("Testing Supervisor Agent...")
    test_input = {
        "user_id": "test_user_123",
        "message": "I want to plan my week",
    }
    
    response = await supervisor_agent.execute(test_input)
    print("\n--- Agent Response ---")
    print(f"Success: {response.success}")
    print(f"Data: {response.data}")
    print(f"Next Agent: {response.next_recommended_agent}")


if __name__ == "__main__":
    asyncio.run(run_test())
