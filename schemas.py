from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

class HomeItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(default=1, ge=1, le=100)

class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    room_type: str = Field(default="Living Room", max_length=80)
    style: str = Field(default="Modern", max_length=80)
    items: List[HomeItem] = Field(default_factory=list)

class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    guests: int = Field(gt=0, le=10_000)
    event_type: str = Field(default="Birthday", max_length=80)
    venue: str = Field(default="Home", max_length=120)
    preferences: str = Field(default="", max_length=1000)

class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    occasion: str = Field(default="Wedding", max_length=80)
    style: str = Field(default="Elegant", max_length=80)
    outfit_color: Optional[str] = Field(default="", max_length=80)
    notes: str = Field(default="", max_length=1000)
