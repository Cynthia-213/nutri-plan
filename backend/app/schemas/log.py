from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from .food import Food  # Import the Food schema for nesting

# --- Log Creation Schemas ---

class FoodLogCreate(BaseModel):
    food_id: int
    serving_grams: float
    log_date: date
    meal_type: str
    total_calories: Optional[float] = None

class ExerciseLogCreate(BaseModel):
    exercise_id: int
    duration_minutes: int
    log_date: date
    calories_burned: Optional[float] = None

# --- Log Response Schemas ---

class FoodLogInDB(FoodLogCreate):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class ExerciseLogInDB(ExerciseLogCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# --- Daily Summary Schemas ---

class LoggedFoodItem(BaseModel):
    food: Food
    serving_grams: float
    meal_type: str
    total_calories: float
    total_protein: float
    total_fat: float
    total_carbs: float

class LoggedExerciseItem(BaseModel):
    exercise_name: str
    duration_minutes: int
    calories_burned: float

class DailySummary(BaseModel):
    log_date: date
    
    # Calorie summary
    bmr: float
    tdee: float
    total_intake_kcal: float
    total_exercise_burned: float
    total_burned_kcal: float
    net_calories: float
    
    # Macronutrient summary
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float
    
    # Detailed logs
    food_log: List[LoggedFoodItem]
    exercise_log: List[LoggedExerciseItem]
    
    # Recommendations
    recommended_daily_kcal: float
    recommended_protein_g: float
    recommended_fat_g: float
    recommended_carbs_g: float
    
    # AI summary
    ai_summary: Optional[str] = None

class CalorieRecommendation(BaseModel):
    goal: str
    recommended_kcal: float
    min_kcal: Optional[float] = None  # 最低热量
    max_kcal: Optional[float] = None  # 最高热量
    protein_g: float
    protein_min_g: Optional[float] = None  # 蛋白质最低值
    protein_max_g: Optional[float] = None  # 蛋白质最高值
    fat_g: float
    fat_min_g: Optional[float] = None  # 脂肪最低值
    fat_max_g: Optional[float] = None  # 脂肪最高值
    carbs_g: float
    range_description: Optional[str] = None  # 区间说明

# --- Energy Summary Schemas ---

class EnergySummaryItem(BaseModel):
    period: str
    total_calories: float

class EnergySummary(BaseModel):
    data: List[EnergySummaryItem]
    bmr: float