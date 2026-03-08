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
    
    if not participants:
        return {"message": "No participants to route", "routes": []}
        
    drivers = [p for p in participants if p.get("drive_priority") in ["will", "must"] and p.get("seats", 0) > 0]
    passengers = [p for p in participants if p.get("drive_priority") == "cannot"]
    
    try:
        event = await db.events.find_one({"_id": ObjectId(event_id)})
    except:
        event = await db.events.find_one({"_id": event_id})
        
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    def haversine(lat1, lon1, lat2, lon2):
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None: return 9999
        R = 3958.8 # Radius of earth in miles
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
    routes = []
    total_emissions = 0.0
    
    # Sort drivers by who is closest to the event
    drivers.sort(key=lambda d: haversine(d.get("address_lat"), d.get("address_lng"), event.get("destination_lat"), event.get("destination_lng")))
    
    for driver in drivers:
        available_seats = driver.get("seats", 4) - 1 # driver takes 1 seat
        assigned_passengers = []
        
        # Sort passengers by who is closest to this driver
        passengers.sort(key=lambda p: haversine(driver.get("address_lat"), driver.get("address_lng"), p.get("address_lat"), p.get("address_lng")))
        
        while available_seats > 0 and passengers:
            closest_passenger = passengers.pop(0)
            assigned_passengers.append(closest_passenger["name"])
            available_seats -= 1
            
        driver_miles = haversine(driver.get("address_lat"), driver.get("address_lng"), event.get("destination_lat"), event.get("destination_lng"))
        if not assigned_passengers: driver_miles *= 1.0 # arbitrary multiplier 
        else: driver_miles *= 1.2 # slightly longer route for pickup
        
        mpg = max(driver.get("mpg_city", 25), 1) 
        gallons = driver_miles / mpg
        emissions = gallons * 8.887 # kg CO2 per gallon
        total_emissions += emissions
            
        routes.append({
            "driver": driver["name"],
            "vehicle": driver.get("car_type", "Unknown"),
            "passengers": assigned_passengers,
            "emissions_kg": round(emissions, 2)
        })
        
    return {
        "status": "success", 
        "total_participants": len(participants),
        "drivers_assigned": len(drivers),
        "passengers_unassigned": len(passengers),
        "total_emissions_kg": round(total_emissions, 2),
        "routes": routes
    }
