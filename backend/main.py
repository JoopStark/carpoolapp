from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from bson import ObjectId

from database import get_db
from models import UserCreate, UserInDB, Token, EventCreate, Event, ParticipantCreate, Participant
from auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    import jwt
    from auth import SECRET_KEY, ALGORITHM
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
        
    user = await db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

@app.post("/register", response_model=Token)
async def register(user: UserCreate, db = Depends(get_db)):
    db_user = await db.users.find_one({"username": user.username})
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]
    
    await db.users.insert_one(user_dict)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = await db.users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "role": current_user.get("role", "participant")}

# --- Events Endpoints ---

@app.post("/events", response_model=Event)
async def create_event(event: EventCreate, current_user: dict = Depends(get_current_user), db = Depends(get_db)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    event_dict = event.dict()
    result = await db.events.insert_one(event_dict)
    event_dict["_id"] = str(result.inserted_id)
    return event_dict

@app.get("/events/current", response_model=List[Event])
async def get_current_events(db = Depends(get_db)):
    cursor = db.events.find({"is_past": False})
    events = await cursor.to_list(length=100)
    for event in events:
        event["_id"] = str(event["_id"])
    return events
    
@app.get("/events/past", response_model=List[Event])
async def get_past_events(db = Depends(get_db)):
    cursor = db.events.find({"is_past": True})
    events = await cursor.to_list(length=100)
    for event in events:
        event["_id"] = str(event["_id"])
    return events

# --- Participants Endpoints ---

@app.post("/events/{event_id}/participants", response_model=Participant)
async def join_event(event_id: str, participant: ParticipantCreate, current_user: dict = Depends(get_current_user), db = Depends(get_db)):
    participant_dict = participant.dict()
    participant_dict["event_id"] = event_id
    participant_dict["user_id"] = str(current_user["_id"])
    
    # Optional: Geocode the participant address here before inserting using a free API
    # (assuming the frontend already sent coords for this MVP)
    
    result = await db.participants.insert_one(participant_dict)
    participant_dict["_id"] = str(result.inserted_id)
    return participant_dict

@app.get("/cars")
async def get_car_options():
    # Mock data for car selector
    return [
        {"id": 1, "make": "Toyota", "model": "Prius", "seats": 4, "mpg_city": 54, "mpg_highway": 50},
        {"id": 2, "make": "Honda", "model": "Civic", "seats": 4, "mpg_city": 31, "mpg_highway": 40},
        {"id": 3, "make": "Ford", "model": "F-150", "seats": 5, "mpg_city": 18, "mpg_highway": 24},
        {"id": 4, "make": "Tesla", "model": "Model 3", "seats": 4, "mpg_city": 138, "mpg_highway": 126}, # MPGe
        {"id": 5, "make": "Subaru", "model": "Outback", "seats": 4, "mpg_city": 26, "mpg_highway": 32},
    ]

# --- Calculation Logic ---

@app.post("/events/{event_id}/calculate")
async def calculate_routes(event_id: str, current_user: dict = Depends(get_current_user), db = Depends(get_db)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    cursor = db.participants.find({"event_id": event_id})
    participants = await cursor.to_list(length=1000)
    
    def haversine(lat1, lon1, lat2, lon2):
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None: return 9999
        R = 3958.8 # Radius of earth in miles
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
    # 1) Separate out the firm requirements
    must_drivers = [p for p in participants if p.get("drive_priority") == "must" and p.get("seats", 0) > 0]
    cannot_passengers = [p for p in participants if p.get("drive_priority") == "cannot"]
    will_drivers = [p for p in participants if p.get("drive_priority") == "will" and p.get("seats", 0) > 0]
    
    # 2) 'will' participants without cars are just passengers
    will_no_car = [p for p in participants if p.get("drive_priority") == "will" and p.get("seats", 0) == 0]
    passengers = cannot_passengers + will_no_car
    
    # 3) We want to use as few cars as possible to minimize emissions.
    # We will sort all potential drivers (must + will) by their MPG (highest first) to prioritize green vehicles
    all_potential_drivers = must_drivers + will_drivers
    all_potential_drivers.sort(key=lambda d: d.get("mpg_city", 25), reverse=True)
    
    drivers = []
    
    # Check if a 'will' driver should actually just be a passenger because a better driver can take them
    for pd in all_potential_drivers:
        # If they MUST drive, they are always a driver
        if pd.get("drive_priority") == "must":
            drivers.append(pd)
            continue
            
        # If they are a 'will' driver, check if any EXISTING driver has space and is close by (e.g. within 5 miles)
        # Note: In a real app we'd also check if adding them doesn't detour too much. For MVP, just distance.
        assigned_as_passenger = False
        for d in drivers:
            # How many seats are left in this driver's car?
            # Seats taken by assigned passengers + the driver themselves
            seats_taken = 1 + len(d.get("_temp_passengers", [])) 
            if seats_taken < d.get("seats", 4):
                if haversine(d.get("address_lat"), d.get("address_lng"), pd.get("address_lat"), pd.get("address_lng")) < 5.0:
                    d.setdefault("_temp_passengers", []).append(pd)
                    assigned_as_passenger = True
                    break
        
        if not assigned_as_passenger:
            pd["_temp_passengers"] = []
            drivers.append(pd)
            
    try:
        event = await db.events.find_one({"_id": ObjectId(event_id)})
    except:
        event = await db.events.find_one({"_id": event_id})
        
    if not event or not isinstance(event, dict):
        raise HTTPException(status_code=404, detail="Event not found")
        
    event_lat = float(event.get("destination_lat", 0.0))
    event_lng = float(event.get("destination_lng", 0.0))

    # Helper function to check if adding a passenger creates an acceptable detour
    # A detour is: (Driver -> Passenger) + (Passenger -> Event) - (Driver -> Event)
    def acceptable_detour(driver_lat, driver_lng, pass_lat, pass_lng, event_lat, event_lng, max_detour_miles=5.0):
        direct = haversine(driver_lat, driver_lng, event_lat, event_lng)
        detour = haversine(driver_lat, driver_lng, pass_lat, pass_lng) + haversine(pass_lat, pass_lng, event_lat, event_lng)
        return (detour - direct) <= max_detour_miles

    # Now that we've solidified who is driving, assign passengers to drivers IF it's efficient
    unassigned_passengers = []
    
    for p in passengers:
        closest_driver = None
        min_detour = float('inf')
        
        for d in drivers:
            if not isinstance(d, dict): continue
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
            
    # If a 'will' passenger got left unassigned due to no efficient driver, they should become a driver
    new_drivers = []
    really_stuck_passengers = []
    for p in unassigned_passengers:
        if not isinstance(p, dict): continue
        if p.get("drive_priority") == "will" and p.get("seats", 0) > 0:
            p["_temp_passengers"] = []
            new_drivers.append(p)
        else:
            really_stuck_passengers.append(p)
    drivers.extend(new_drivers)
            
    routes = []
    total_emissions = 0.0
    passengers_unassigned = len(really_stuck_passengers)
    
    for driver in drivers:
        if not isinstance(driver, dict): continue
        driver_lat = float(driver.get("address_lat", 0.0))
        driver_lng = float(driver.get("address_lng", 0.0))
        
        assigned_passengers = [p.get("name") for p in driver.get("_temp_passengers", []) if isinstance(p, dict)]
        
        # Calculate true miles
        # For simplicity, we just add the distance sequentially Driver -> P1 -> P2 -> Event
        # Sorting passengers by distance from driver to somewhat optimize the TSP
        pass_list = [p for p in driver.get("_temp_passengers", []) if isinstance(p, dict)]
        pass_list.sort(key=lambda p: float(haversine(driver_lat, driver_lng, float(p.get("address_lat", 0.0)), float(p.get("address_lng", 0.0)))))
        
        driver_miles = 0.0
        current_lat, current_lng = driver_lat, driver_lng
        
        for p in pass_list:
            p_lat = float(p.get("address_lat", 0.0))
            p_lng = float(p.get("address_lng", 0.0))
            driver_miles += haversine(current_lat, current_lng, p_lat, p_lng)
            current_lat, current_lng = p_lat, p_lng
            
        # Finally, to the event
        driver_miles += haversine(current_lat, current_lng, event_lat, event_lng)
        
        mpg = max(float(driver.get("mpg_city", 25.0)), 1.0) 
        gallons = driver_miles / mpg
        emissions = float(gallons * 8.887) # kg CO2 per gallon
        total_emissions += emissions
            
        routes.append({
            "driver": driver.get("name", "Unknown"),
            "vehicle": driver.get("car_type", "Unknown"),
            "passengers": assigned_passengers,
            "emissions_kg": round(float(emissions), 2)
        })
        
    baseline_emissions = 0.0
    for p in participants:
        if not isinstance(p, dict): continue
        p_lat = float(p.get("address_lat", 0.0))
        p_lng = float(p.get("address_lng", 0.0))
        
        p_miles = haversine(p_lat, p_lng, event_lat, event_lng)
        # If they don't have a car, assume they take an Uber (approx 25 mpg)
        p_mpg = max(float(p.get("mpg_city") or 25.0), 1.0)
        p_gallons = p_miles / p_mpg
        baseline_emissions += p_gallons * 8.887
        
    return {
        "status": "success", 
        "total_participants": len(participants) if participants else 0,
        "drivers_assigned": len(drivers),
        "passengers_unassigned": max(0, passengers_unassigned),
        "total_emissions_kg": round(float(total_emissions), 2),
        "baseline_emissions_kg": round(float(baseline_emissions), 2),
        "routes": routes
    }
