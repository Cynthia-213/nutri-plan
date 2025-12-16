from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from .food import Food  # Import the Food schema for nesting

# --- Log Creation Schemas ---

class FoodLogCreate(BaseModel):
    food_id: int
    serving_grams: float
    log_date: date

class ExerciseLogCreate(BaseModel):
    exercise_id: int
    duration_minutes: int
    log_date: date

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
    total_intake_kcal: float
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
    protein_g: float
    fat_g: float
    carbs_g: float

# --- Energy Summary Schemas ---

class EnergySummaryItem(BaseModel):
    period: str
    total_calories: float

class EnergySummary(BaseModel):
    data: List[EnergySummaryItem]
