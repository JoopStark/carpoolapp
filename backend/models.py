from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    role: str = "participant" # 'admin' or 'participant'

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

class User(UserBase):
    id: str = Field(alias="_id")

class EventBase(BaseModel):
    name: str
    destination_address: str
    destination_lat: float
    destination_lng: float
    start_time: datetime
    is_past: bool = False

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: str = Field(alias="_id")

class ParticipantBase(BaseModel):
    event_id: Optional[str] = None
    user_id: Optional[str] = None
    name: str
    address: str
    address_lat: float
    address_lng: float
    car_type: Optional[str] = None
    seats: int = 0
    mpg_city: float = 0.0
    mpg_highway: float = 0.0
    arrival_buffer_mins: int = 0
    drive_priority: str # 'cannot', 'will', 'must'

class ParticipantCreate(ParticipantBase):
    pass

class Participant(ParticipantBase):
    id: str = Field(alias="_id")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
