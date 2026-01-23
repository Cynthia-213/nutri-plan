from sqlalchemy import Column, Integer, DECIMAL, Date, TIMESTAMP, text, ForeignKey, Text
from sqlalchemy.orm import relationship
from .user import Base


class BodyMetrics(Base):
    """
    用户身体指标历史记录表
    用于记录体重、体脂率等指标的变化历史
    """
    __tablename__ = "body_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_date = Column(Date, nullable=False, comment='记录日期')
    weight_kg = Column(DECIMAL(5, 2), nullable=True, comment='体重（公斤）')
    body_fat_pct = Column(DECIMAL(4, 2), nullable=True, comment='体脂率（百分比）')
    muscle_mass_kg = Column(DECIMAL(5, 2), nullable=True, comment='肌肉量（公斤，可选）')
    notes = Column(Text, nullable=True, comment='备注')
    
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    user = relationship("User", backref="body_metrics")
