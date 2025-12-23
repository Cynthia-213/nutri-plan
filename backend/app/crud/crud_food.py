from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.food import Food
from app.schemas.food import FoodCreate

class CRUDFood:
    def get_food_by_id(self, db: Session, *, food_id: int) -> Optional[Food]:
        """通过ID获取食物"""
        return db.query(Food).filter(Food.id == food_id).first()
        
    def search_foods(self, db: Session, *, keyword: str, skip: int = 0, limit: int = 100) -> List[Food]:
        """根据关键词搜索食物"""
        return db.query(Food).filter(
            or_(
                Food.description_en.ilike(f"%{keyword}%"),
                Food.description_zh.ilike(f"%{keyword}%")
            )
        ).offset(skip).limit(limit).all()

    def count_foods(self, db: Session, *, keyword: str) -> int:
        """计算搜索结果的总数"""
        return db.query(Food).filter(
            or_(
                Food.description_en.ilike(f"%{keyword}%"),
                Food.description_zh.ilike(f"%{keyword}%")
            )
        ).count()
    def create(self, db: Session, *, obj_in: FoodCreate) -> Food:
        """创建新食物"""
        obj_in_data = obj_in.model_dump()
        if 'source' not in obj_in_data or not obj_in_data['source']:
            obj_in_data['source'] = 'user'
        db_obj = Food(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

# 创建一个实例以便全局使用
food = CRUDFood()