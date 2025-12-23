from sqlalchemy import Column, BIGINT, String, DECIMAL, TIMESTAMP, text
from sqlalchemy.orm import relationship
from .user import Base

class Food(Base):
    __tablename__ = "foods"

    id = Column(BIGINT, primary_key=True)
    description_zh = Column(String(255), unique=True)
    description_en = Column(String(255))
    
    energy_kcal = Column(DECIMAL(10, 2))
    protein_g = Column(DECIMAL(10, 2))
    fat_g = Column(DECIMAL(10, 2))
    carbohydrate_g = Column(DECIMAL(10, 2))
    fiber_total_dietary_g = Column(DECIMAL(10, 2))
    sugars_g = Column(DECIMAL(10, 2))
    fe_mg = Column(DECIMAL(10, 2))
    na_mg = Column(DECIMAL(10, 2))
    
    serving_size_g = Column(DECIMAL(10, 2), server_default='100.00')

    source = Column(String(100))

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    food_logs = relationship("UserFoodLog", back_populates="food")    