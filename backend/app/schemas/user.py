from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from enum import Enum

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


# 用户共享属性
class UserBase(BaseModel):
    email: EmailStr
    username: str
    gender: GenderEnum = None
    birthdate: Optional[date] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[ActivityLevelEnum] = None
    goal: Optional[GoalEnum] = None


# 创建用户时所需属性
class UserCreate(UserBase):
    password: str

# 用户登录时所需属性
class UserLogin(BaseModel):
    username: str
    password: str

# 用户可更新的属性
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[GenderEnum] = None
    birthdate: Optional[date] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[ActivityLevelEnum] = None
    goal: Optional[GoalEnum] = None

# 数据库中存储的其他属性（例如 hashed_pa​​ssword）
class UserInDB(UserBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True

# 要返回给客户端的属性（省略敏感数据）
class User(UserBase):
    id: int

    class Config:
        from_attributes = True