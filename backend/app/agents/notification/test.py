import asyncio
import sys
from app.agents.notification.agent import notification_agent

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


async def run_test():
    print("Testing Notification Agent...")
    test_input = {
        "user_id": "test_user_123",
        "event_type": "reflection_submitted",
        "risk_level": "high",
    }
    
    response = await notification_agent.execute(test_input)
    print("\n--- Agent Response ---")
    print(f"Success: {response.success}")
    print(f"Data: {response.data}")
    print(f"Database Updates: {response.database_updates}")


if __name__ == "__main__":
    asyncio.run(run_test())
