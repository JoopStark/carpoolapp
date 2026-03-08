import asyncio
from database import db
from bson import ObjectId
import math

async def test_calculate():
    # Find the current event
    event = await db.events.find_one({"is_past": False})
    if not event:
        print("No active event found.")
        return
        
    event_id = str(event["_id"])
    print(f"Testing calculation for event {event_id}: {event.get('name')}")
    
    # Just grab all participants to see how the logic groups them
    cursor = db.participants.find({"event_id": event_id})
    participants = await cursor.to_list(length=100)
    print(f"Found {len(participants)} participants.")
    
    # The logic from main.py:
    must_drivers = [p for p in participants if p.get("drive_priority") == "must" and p.get("seats", 0) > 0]
    cannot_passengers = [p for p in participants if p.get("drive_priority") == "cannot"]
    will_drivers = [p for p in participants if p.get("drive_priority") == "will" and p.get("seats", 0) > 0]
    will_no_car = [p for p in participants if p.get("drive_priority") == "will" and p.get("seats", 0) == 0]
    passengers = cannot_passengers + will_no_car
    
    all_potential_drivers = must_drivers + will_drivers
    all_potential_drivers.sort(key=lambda d: d.get("mpg_city", 25), reverse=True)
    
    drivers = []
    
    def haversine(lat1, lon1, lat2, lon2):
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None: return 9999
        R = 3958.8 
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    for pd in all_potential_drivers:
        if pd.get("drive_priority") == "must":
            drivers.append(pd)
            continue
            
        assigned_as_passenger = False
        for d in drivers:
            seats_taken = 1 + len(d.get("_temp_passengers", [])) 
            if seats_taken < d.get("seats", 4):
                if haversine(d.get("address_lat"), d.get("address_lng"), pd.get("address_lat"), pd.get("address_lng")) < 5.0:
                    d.setdefault("_temp_passengers", []).append(pd)
                    assigned_as_passenger = True
                    break
        
        if not assigned_as_passenger:
            pd["_temp_passengers"] = []
            drivers.append(pd)
            
    # Helper function to check if adding a passenger creates an acceptable detour
    # A detour is: (Driver -> Passenger) + (Passenger -> Event) - (Driver -> Event)
    def acceptable_detour(driver_lat, driver_lng, pass_lat, pass_lng, event_lat, event_lng, max_detour_miles=0.5):
        direct = haversine(driver_lat, driver_lng, event_lat, event_lng)
        detour = haversine(driver_lat, driver_lng, pass_lat, pass_lng) + haversine(pass_lat, pass_lng, event_lat, event_lng)
        return (detour - direct) <= max_detour_miles

    unassigned_passengers = []
    event_lat = float(event.get("destination_lat", 0.0))
    event_lng = float(event.get("destination_lng", 0.0))
    
    for p in passengers:
        closest_driver = None
        min_detour = float('inf')
        
        for d in drivers:
            seats_taken = 1 + len(d.get("_temp_passengers", []))
            if seats_taken < (d.get("seats") or 4):
                d_lat = float(d.get("address_lat", 0.0))
                d_lng = float(d.get("address_lng", 0.0))
                p_lat = float(p.get("address_lat", 0.0))
                p_lng = float(p.get("address_lng", 0.0))
                
                if acceptable_detour(d_lat, d_lng, p_lat, p_lng, event_lat, event_lng):
                    direct = haversine(d_lat, d_lng, event_lat, event_lng)
                    detour = haversine(d_lat, d_lng, p_lat, p_lng) + haversine(p_lat, p_lng, event_lat, event_lng)
                    detour_cost = float(detour - direct)
                    
                    if detour_cost < min_detour:
                        min_detour = detour_cost
                        closest_driver = d
                    
        if closest_driver and isinstance(closest_driver, dict):
            if "_temp_passengers" not in closest_driver:
                closest_driver["_temp_passengers"] = []
            closest_driver["_temp_passengers"].append(p)
        else:
            unassigned_passengers.append(p)

    new_drivers = []
    for p in unassigned_passengers:
        if p.get("drive_priority") == "will" and p.get("seats", 0) > 0:
            p["_temp_passengers"] = []
            new_drivers.append(p)
    drivers.extend(new_drivers)

    print(f"\nResults:")
    print(f"Total drivers deployed: {len(drivers)}")
    for d in drivers:
        passengers_names = [p.get("name", "Unknown") for p in d.get("_temp_passengers", []) if isinstance(p, dict)]
        print(f"Driver: {d.get('name')} | Passengers: {passengers_names}")

if __name__ == "__main__":
    asyncio.run(test_calculate())
