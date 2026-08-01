"""Test script for Reflection Agent."""
import asyncio
from app.agents.reflection.agent import reflection_agent


async def run_test():
    print("Testing Reflection Agent...")
    test_input = {
        "user_id": "test_user_123",
        "mood_score": 2,
        "energy_level": 1,
        "study_hours": 8.0,
        "completed_tasks": ["task1", "task2"],
        "reflection": "Feeling completely exhausted today.",
    }
    
    response = await reflection_agent.execute(test_input)
    print("\n--- Agent Response ---")
    print(f"Success: {response.success}")
    print(f"Data: {response.data}")
    print(f"Memory Updates: {response.memory_updates}")
    print(f"Database Updates: {response.database_updates}")
    print(f"Next Agent: {response.next_recommended_agent}")


if __name__ == "__main__":
    asyncio.run(run_test())
