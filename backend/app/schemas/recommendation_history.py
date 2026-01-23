from pydantic import BaseModel
from datetime import date
from typing import Optional, List, Dict, Any


class RecommendationHistoryCreate(BaseModel):
    """创建推荐调整记录"""
    adjustment_date: date
    previous_kcal: Optional[float] = None
    previous_protein_g: Optional[float] = None
    previous_fat_g: Optional[float] = None
    previous_carbs_g: Optional[float] = None
    new_kcal: Optional[float] = None
    new_protein_g: Optional[float] = None
    new_fat_g: Optional[float] = None
    new_carbs_g: Optional[float] = None
    adjustment_reason: Optional[str] = None
    trigger_factors: Optional[Dict[str, Any]] = None


class RecommendationHistoryInDB(BaseModel):
    """数据库中的推荐调整记录"""
    id: int
    user_id: int
    adjustment_date: date
    previous_kcal: Optional[float] = None
    previous_protein_g: Optional[float] = None
    previous_fat_g: Optional[float] = None
    previous_carbs_g: Optional[float] = None
    new_kcal: Optional[float] = None
    new_protein_g: Optional[float] = None
    new_fat_g: Optional[float] = None
    new_carbs_g: Optional[float] = None
    adjustment_reason: Optional[str] = None
    trigger_factors: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class RecommendationHistoryResponse(BaseModel):
    """推荐调整历史响应"""
    data: List[RecommendationHistoryInDB]
    total_records: int
