from sqlalchemy import Column, Integer, BIGINT, TIMESTAMP, text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .user import Base

class UserBannedFood(Base):
    __tablename__ = "user_banned_foods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    food_id = Column(BIGINT, ForeignKey("foods.id"), nullable=False, index=True)
    
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # 确保同一用户不能重复添加同一个食物
    __table_args__ = (
        UniqueConstraint('user_id', 'food_id', name='uq_user_banned_food'),
    )
    
    # Relationships
    user = relationship("User", backref="banned_foods")
    food = relationship("Food", backref="banned_by_users")
