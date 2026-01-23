from sqlalchemy import Column, Integer, DECIMAL, Date, TIMESTAMP, text, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .user import Base


class RecommendationHistory(Base):
    """
    推荐调整历史记录表
    记录每次推荐调整的详细信息
    """
    __tablename__ = "recommendation_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    adjustment_date = Column(Date, nullable=False, comment='调整日期')
    
    # 调整前的推荐值
    previous_kcal = Column(DECIMAL(8, 2), nullable=True, comment='调整前热量')
    previous_protein_g = Column(DECIMAL(6, 2), nullable=True, comment='调整前蛋白质（克）')
    previous_fat_g = Column(DECIMAL(6, 2), nullable=True, comment='调整前脂肪（克）')
    previous_carbs_g = Column(DECIMAL(6, 2), nullable=True, comment='调整前碳水化合物（克）')
    
    # 调整后的推荐值
    new_kcal = Column(DECIMAL(8, 2), nullable=True, comment='调整后热量')
    new_protein_g = Column(DECIMAL(6, 2), nullable=True, comment='调整后蛋白质（克）')
    new_fat_g = Column(DECIMAL(6, 2), nullable=True, comment='调整后脂肪（克）')
    new_carbs_g = Column(DECIMAL(6, 2), nullable=True, comment='调整后碳水化合物（克）')
    
    adjustment_reason = Column(Text, nullable=True, comment='调整原因')
    trigger_factors = Column(JSON, nullable=True, comment='触发调整的因素（JSON格式）')
    
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    user = relationship("User", backref="recommendation_history")
