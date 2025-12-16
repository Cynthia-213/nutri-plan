from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, text
from sqlalchemy.orm import relationship
from .user import Base  # 假设所有模型都使用同一个Base

class Food(Base):
    __tablename__ = "foods_information"

    id = Column(Integer, primary_key=True, index=True)
    fdc_id = Column(Integer, unique=True, index=True)
    description = Column(String(255), nullable=False)
    category = Column(String(255))
    
    energy_kcal = Column(DECIMAL(10, 2))
    protein_g = Column(DECIMAL(10, 2))
    fat_g = Column(DECIMAL(10, 2))
    carbohydrate_g = Column(DECIMAL(10, 2))
    
    serving_size_g = Column(DECIMAL(10, 2), server_default='100.00')

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    # Define relationship to UserFoodLog model
    food_logs = relationship("UserFoodLog", back_populates="food")
