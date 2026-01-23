from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from enum import Enum

class GenderEnum(str, Enum):
    male = 'male'
    female = 'female'

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
    gain_weight = 'gain_weight'
    body_recomposition = 'body_recomposition'

class TrainingExperienceEnum(str, Enum):
    beginner = 'beginner'
    intermediate = 'intermediate'
    advanced = 'advanced'

class IdentityEnum(str, Enum):
    student = 'student'  # 学生族
    office_worker = 'office_worker'  # 职场办公人
    flexible = 'flexible'  # 自由职业/居家
    fitness_pro = 'fitness_pro'  # 健身达人
    health_care = 'health_care'  # 康养人群


# 用户共享属性
class UserBase(BaseModel):
    email: EmailStr
    username: str
    gender: GenderEnum
    birthdate: date
    height_cm: float
    weight_kg: float
    activity_level: ActivityLevelEnum
    goal: GoalEnum
    body_fat_pct: Optional[float] = None
    training_experience: TrainingExperienceEnum = TrainingExperienceEnum.beginner
    last_period_start: Optional[date] = None
    enable_periodized_nutrition: Optional[str] = 'false'
    identity: IdentityEnum


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
    body_fat_pct: Optional[float] = None
    training_experience: Optional[TrainingExperienceEnum] = None
    last_period_start: Optional[date] = None
    enable_periodized_nutrition: Optional[str] = None
    identity: Optional[IdentityEnum] = None

# 修改密码
class PasswordChange(BaseModel):
    old_password: str
    new_password: str

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