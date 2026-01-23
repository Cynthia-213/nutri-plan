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
    
    gender = Column(Enum('male', 'female'), nullable=False)
    birthdate = Column(Date, nullable=False)
    height_cm = Column(DECIMAL(5, 2), nullable=False)
    weight_kg = Column(DECIMAL(5, 2), nullable=False)
    
    activity_level = Column(
        Enum('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active'),
        nullable=False,
        server_default='sedentary'
    )
    goal = Column(
        Enum('maintain', 'lose_weight', 'gain_muscle', 'gain_weight', 'body_recomposition'),
        nullable=False,
        server_default='maintain'
    )
    
    body_fat_pct = Column(DECIMAL(4, 2), nullable=True, comment='体脂率（百分比）')
    training_experience = Column(
        Enum('beginner', 'intermediate', 'advanced'),
        nullable=False,
        server_default='beginner',
        comment='训练经验'
    )
    last_period_start = Column(Date, nullable=True, comment='上次月经开始日期（仅女性）')
    enable_periodized_nutrition = Column(
        String(10),
        nullable=False,
        server_default='false',
        comment='是否启用周期化营养（训练日/休息日）'
    )
    
    identity = Column(
        Enum('student', 'office_worker', 'flexible', 'fitness_pro', 'health_care'),
        nullable=False,
        server_default='office_worker'
    )
    
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
