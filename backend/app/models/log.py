from sqlalchemy import Column, Integer, DECIMAL, Date, TIMESTAMP, text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .user import Base
from .food import Food
from .exercise import Exercise

class UserFoodLog(Base):
    __tablename__ = "user_food_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    serving_grams = Column(DECIMAL(10, 2), nullable=False)
    meal_type = Column(Enum('breakfast', 'lunch', 'dinner', 'snack'), nullable=False)
    total_calories = Column(DECIMAL(8, 2))
    log_date = Column(Date, nullable=False)
    
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    user = relationship("User")
    food = relationship("Food", back_populates="food_logs")

class UserExerciseLog(Base):
    __tablename__ = "user_exercise_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    calories_burned = Column(DECIMAL(7, 2), nullable=False)
    log_date = Column(Date, nullable=False)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    user = relationship("User")
    exercise = relationship("Exercise", back_populates="exercise_logs")
