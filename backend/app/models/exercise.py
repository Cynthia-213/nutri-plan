from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, Text, text
from sqlalchemy.orm import relationship
from .user import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    met_value = Column(DECIMAL(4, 2), nullable=False)
    description = Column(Text)
    
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Define relationship to UserExerciseLog model
    exercise_logs = relationship("UserExerciseLog", back_populates="exercise")
