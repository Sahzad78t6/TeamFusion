"""Test script for Planner Agent."""
import asyncio
from app.agents.planner.agent import planner_agent


async def run_test():
    print("Testing Planner Agent...")
    test_input = {
        "user_id": "test_user_123",
        "goals": ["Learn advanced FastAPI", "Deploy to AWS"],
    }
    
    response = await planner_agent.execute(test_input)
    print("\n--- Agent Response ---")
    print(f"Success: {response.success}")
    print(f"Data: {response.data}")
    print(f"Database Updates: {response.database_updates}")
    print(f"Next Agent: {response.next_recommended_agent}")


if __name__ == "__main__":
    asyncio.run(run_test())
