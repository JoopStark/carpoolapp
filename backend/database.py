import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.carpool_db

from motor.motor_asyncio import AsyncIOMotorDatabase

async def get_db() -> AsyncIOMotorDatabase:
    return db
