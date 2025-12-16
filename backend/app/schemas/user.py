from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from enum import Enum

# --- Enums for validation ---
# These should match the enums in the database model
class GenderEnum(str, Enum):
    male = 'male'
    female = 'female'
    unwilling_to_disclose = 'unwilling_to_disclose'

class ActivityLevelEnum(str, Enum):
    sedentary = 'sedentary'
    lightly_active = 'lightly_active'
    moderately_active = 'moderately_active'
    very_active = 'very_active'
    extra_active = 'extra_active'

class GoalEnum(str, Enum):
    maintain = 'maintain'
    lose_weight = 'lose_weight'
    gain_muscle = 'gain_muscle'


# --- Base Schema ---
# Shared properties for a user
class UserBase(BaseModel):
    email: EmailStr
    username: str
    gender: Optional[GenderEnum] = None
    birthdate: Optional[date] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[ActivityLevelEnum] = None
    goal: Optional[GoalEnum] = None


# --- Create Schema ---
# Properties required when creating a new user
class UserCreate(UserBase):
    password: str


# --- Update Schema ---
# Properties that can be updated for a user
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[GenderEnum] = None
    birthdate: Optional[date] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[ActivityLevelEnum] = None
    goal: Optional[GoalEnum] = None


# --- Database Schema ---
# Additional properties stored in the database (like hashed_password)
class UserInDB(UserBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True


# --- Response Schema ---
# Properties to return to the client (omitting sensitive data)
class User(UserBase):
    id: int

    class Config:
        from_attributes = True

