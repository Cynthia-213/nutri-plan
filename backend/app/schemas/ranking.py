"""
排行榜相关的Schema定义
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class RankingItem(BaseModel):
    """排行榜单项"""
    user_id: int
    username: Optional[str] = None
    calories: float
    rank: int
    identity: Optional[str] = None  # 用户身份，用于显示身份图标

    class Config:
        from_attributes = True


class UserRankingInfo(BaseModel):
    """用户排名信息"""
    user_id: int
    rank: Optional[int] = None  # None表示不在榜上
    calories: Optional[float] = None

    class Config:
        from_attributes = True


class RankingResponse(BaseModel):
    """排行榜响应"""
    rankings: List[RankingItem]
    user_ranking: Optional[UserRankingInfo] = None
    period: str  # 'day', 'month', 'year'
    identity: Optional[str] = None  # None表示总榜
    target_date: date

    class Config:
        from_attributes = True
