import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

async def test_connection():
    print(f"Connecting to: {MONGO_URI}")
    client = AsyncIOMotorClient(
        MONGO_URI, 
        serverSelectionTimeoutMS=5000, 
        tlsCAFile=certifi.where()
    )
    try:
        info = await client.server_info()
        print("Connected successfully!")
    except Exception as e:
        print("Failed to connect:")
        print(e)

if __name__ == "__main__":
    asyncio.run(test_connection())
