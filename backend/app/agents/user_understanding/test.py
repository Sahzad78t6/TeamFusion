"""Test script for User Understanding Agent."""
import asyncio
from app.agents.user_understanding.agent import user_understanding_agent


async def run_test():
    print("Testing User Understanding Agent...")
    test_input = {
        "user_id": "test_user_123",
        "goal": "Become a Senior Machine Learning Engineer",
        "skills": ["Python", "Pandas", "Scikit-Learn"],
        "interests": ["Deep Learning", "NLP"],
    }
    
    response = await user_understanding_agent.execute(test_input)
    print("\n--- Agent Response ---")
    print(f"Success: {response.success}")
    print(f"Data: {response.data}")
    print(f"Memory Updates: {response.memory_updates}")
    print(f"Database Updates: {response.database_updates}")


if __name__ == "__main__":
    asyncio.run(run_test())
