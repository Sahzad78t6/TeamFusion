import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

async def test_mongo():
    print(f"Testing MongoDB connection to: {settings.MONGODB_URL}")
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        res = await client.admin.command('ping')
        print("[SUCCESS] Ping successful! Result:", res)
        db = client[settings.MONGODB_DB_NAME]
        cols = await db.list_collection_names()
        print("[SUCCESS] Collections:", cols)
        client.close()
        return True
    except Exception as e:
        print("[ERROR] MongoDB Connection Error:", type(e).__name__, str(e))
        return False

if __name__ == "__main__":
    asyncio.run(test_mongo())
