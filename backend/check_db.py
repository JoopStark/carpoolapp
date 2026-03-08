import asyncio
from database import db
async def check():
    cursor = db.participants.find({"name": {"$in": ["alpha", "bravo", "charlie", "delta"]}})
    for p in await cursor.to_list(length=10):
        print(f"{p['name']}: {p['address_lat']}, {p['address_lng']}")
asyncio.run(check())
