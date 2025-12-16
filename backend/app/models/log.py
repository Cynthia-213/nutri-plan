from sqlalchemy import Column, Integer, DECIMAL, Date, TIMESTAMP, text, ForeignKey
from sqlalchemy.orm import relationship
from .user import Base
from .food import Food # Import the Food model
from .exercise import Exercise # Import the Exercise model

class UserFoodLog(Base):
    __tablename__ = "user_food_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    food_id = Column(Integer, ForeignKey("foods_information.id"), index=True, nullable=False) # Add ForeignKey
    serving_grams = Column(DECIMAL(10, 2), nullable=False)
    log_date = Column(Date, nullable=False, index=True)
    
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Define relationship to Food model
    food = relationship("Food", back_populates="food_logs") # Establish back_populates

class UserExerciseLog(Base):
    __tablename__ = "user_exercise_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), index=True, nullable=False) # Add ForeignKey
    duration_minutes = Column(Integer, nullable=False)
    log_date = Column(Date, nullable=False, index=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Define relationship to Exercise model
    exercise = relationship("Exercise", back_populates="exercise_logs")
