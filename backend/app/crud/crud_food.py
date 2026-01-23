from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from typing import List, Optional
import random

from app.models.food import Food
from app.schemas.food import FoodCreate
from app.crud.crud_banned_food import banned_food

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
    
    def get_ai_candidates(self, db: Session, *, preference: str = "balanced", user_id: Optional[int] = None) -> List[Food]:
        """
        根据用户偏好获取约 150 种候选食物
        如果提供了 user_id，会排除该用户禁止的食物
        """
        configs = {
            "high_protein": {"protein": 70, "carbs": 30, "veg": 50},
            "low_carb":     {"protein": 50, "carbs": 20, "veg": 80},
            "balanced":     {"protein": 50, "carbs": 50, "veg": 50}
        }
        
        cfg = configs.get(preference, configs["balanced"])
        candidates = []

        # 获取用户禁止的食物ID列表
        banned_food_ids = []
        if user_id:
            banned_food_ids = banned_food.get_banned_food_ids(db, user_id=user_id)

        # 构建基础查询，排除禁止的食物
        base_query = db.query(Food)
        if banned_food_ids:
            base_query = base_query.filter(~Food.id.in_(banned_food_ids))

        # 1. 采样高蛋白食材 (肉蛋奶鱼)
        protein_query = base_query.filter(Food.is_high_protein == True)
        protein_foods = protein_query.order_by(func.rand()).limit(cfg["protein"]).all()
        
        # 2. 采样主食/碳水 (且相对低脂)
        carb_query = base_query.filter(Food.carbohydrate_g > 20, Food.is_low_fat == True)
        carb_foods = carb_query.order_by(func.rand()).limit(cfg["carbs"]).all()
        
        # 3. 采样蔬菜/高纤维
        veg_query = base_query.filter(or_(Food.is_high_fiber == True, Food.description_zh.contains("菜")))
        veg_foods = veg_query.order_by(func.rand()).limit(cfg["veg"]).all()

        # 合并所有食材
        candidates = protein_foods + carb_foods + veg_foods
        random.shuffle(candidates) # 再次打乱，防止返回时分类感太强
        return candidates

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