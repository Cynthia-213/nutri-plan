from sqlalchemy import Column, Integer, String, Enum, Date, DECIMAL, TIMESTAMP, text
from sqlalchemy.orm import declarative_base

# 创建一个所有模型都会继承的基础类
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    gender = Column(Enum('male', 'female', 'unwilling_to_disclose'))
    birthdate = Column(Date)
    height_cm = Column(DECIMAL(5, 2))
    weight_kg = Column(DECIMAL(5, 2))
    
    activity_level = Column(
        Enum('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active'),
        nullable=False,
        server_default='sedentary'
    )
    goal = Column(
        Enum('maintain', 'lose_weight', 'gain_muscle'),
        nullable=False,
        server_default='maintain'
    )
    
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
