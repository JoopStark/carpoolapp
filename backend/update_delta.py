import asyncio
from database import db
async def update():
    await db.participants.update_one(
        {"name": "delta"}, 
        {"$set": {"address_lat": 40.8500, "address_lng": -73.8000}} # different lat/lng
    )
    print("Updated Delta's coordinates")
asyncio.run(update())
