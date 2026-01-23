from pydantic import BaseModel
from datetime import date
from typing import Optional, List


class BodyMetricsCreate(BaseModel):
    """创建身体指标记录"""
    record_date: date
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    notes: Optional[str] = None


class BodyMetricsUpdate(BaseModel):
    """更新身体指标记录"""
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    notes: Optional[str] = None


class BodyMetricsInDB(BaseModel):
    """数据库中的身体指标记录"""
    id: int
    user_id: int
    record_date: date
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class BodyMetricsTrend(BaseModel):
    """身体指标趋势"""
    record_date: date
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    weight_change_kg: Optional[float] = None  # 相对于上次的变化
    body_fat_change_pct: Optional[float] = None  # 相对于上次的变化


class BodyMetricsTrendResponse(BaseModel):
    """身体指标趋势响应"""
    data: List[BodyMetricsTrend]
    total_records: int
