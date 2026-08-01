"""Test script for Learning Curator Agent."""
import asyncio
from app.agents.learning_curator.agent import learning_curator_agent


async def run_test():
    print("Testing Learning Curator Agent...")
    test_input = {
        "user_id": "test_user_123",
    }
    
    response = await learning_curator_agent.execute(test_input)
    print("\n--- Agent Response ---")
    print(f"Success: {response.success}")
    print(f"Data: {response.data}")
    print(f"Database Updates: {response.database_updates}")
    print(f"Next Agent: {response.next_recommended_agent}")


if __name__ == "__main__":
    asyncio.run(run_test())
