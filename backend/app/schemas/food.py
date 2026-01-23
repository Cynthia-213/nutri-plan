from pydantic import BaseModel
from typing import Optional, List

# 基础属性
class FoodBase(BaseModel):
    description_zh: Optional[str] = None
    description_en: Optional[str] = None
    energy_kcal: Optional[float] = None
    protein_g: Optional[float] = None
    fat_g: Optional[float] = None
    carbohydrate_g: Optional[float] = None
    fiber_total_dietary_g: Optional[float] = None
    sugars_g: Optional[float] = None
    fe_mg: Optional[float] = None
    na_mg: Optional[float] = None
    serving_size_g: Optional[float] = 100.0
    source: Optional[str] = None

# 返回给客户端的食物模型 (带 ID)
class Food(FoodBase):
    id: int
    class Config:
        from_attributes = True

# 分页容器模型 (重要：不要继承 FoodBase)
class FoodPagination(BaseModel):
    total: int
    items: List[Food]
    
    class Config:
        from_attributes = True

# 创建模型
class FoodCreate(FoodBase):
    description_zh: str 

# 更新模型
class FoodUpdate(FoodBase):
    pass

# 禁止食物相关模型
class BannedFoodCreate(BaseModel):
    food_id: int

class BannedFood(BaseModel):
    id: int
    user_id: int
    food_id: int
    food: Optional[Food] = None  # 关联的食物信息
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True

class BannedFoodList(BaseModel):
    items: List[BannedFood]
    total: int
    
    class Config:
        from_attributes = True