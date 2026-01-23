from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from sqlalchemy.exc import IntegrityError

from app.models.user_banned_food import UserBannedFood
from app.models.food import Food
from app.schemas.food import BannedFoodCreate

class CRUDBannedFood:
    def create(self, db: Session, *, user_id: int, banned_food_in: BannedFoodCreate) -> Optional[UserBannedFood]:
        """添加禁止的食物"""
        # 检查食物是否存在
        food = db.query(Food).filter(Food.id == banned_food_in.food_id).first()
        if not food:
            return None
        
        # 检查是否已经存在
        existing = db.query(UserBannedFood).filter(
            UserBannedFood.user_id == user_id,
            UserBannedFood.food_id == banned_food_in.food_id
        ).first()
        if existing:
            return existing
        
        # 创建新的禁止食物记录
        db_banned_food = UserBannedFood(
            user_id=user_id,
            food_id=banned_food_in.food_id
        )
        db.add(db_banned_food)
        try:
            db.commit()
            db.refresh(db_banned_food)
            return db_banned_food
        except IntegrityError:
            db.rollback()
            return None

    def get_by_user(self, db: Session, *, user_id: int) -> List[UserBannedFood]:
        """获取用户的所有禁止食物"""
        return db.query(UserBannedFood).options(
            joinedload(UserBannedFood.food)
        ).filter(UserBannedFood.user_id == user_id).all()

    def get_banned_food_ids(self, db: Session, *, user_id: int) -> List[int]:
        """获取用户禁止的食物ID列表（用于查询过滤）"""
        banned_foods = db.query(UserBannedFood.food_id).filter(
            UserBannedFood.user_id == user_id
        ).all()
        return [bf[0] for bf in banned_foods]

    def delete(self, db: Session, *, user_id: int, food_id: int) -> bool:
        """删除禁止的食物"""
        banned_food = db.query(UserBannedFood).filter(
            UserBannedFood.user_id == user_id,
            UserBannedFood.food_id == food_id
        ).first()
        
        if not banned_food:
            return False
        
        db.delete(banned_food)
        db.commit()
        return True

    def is_banned(self, db: Session, *, user_id: int, food_id: int) -> bool:
        """检查某个食物是否被用户禁止"""
        banned_food = db.query(UserBannedFood).filter(
            UserBannedFood.user_id == user_id,
            UserBannedFood.food_id == food_id
        ).first()
        return banned_food is not None

# 创建一个实例以便全局使用
banned_food = CRUDBannedFood()
