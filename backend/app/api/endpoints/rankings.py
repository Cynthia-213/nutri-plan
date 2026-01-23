"""
排行榜API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, Any

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.crud.crud_user import user as crud_user
from app.schemas.ranking import RankingResponse, RankingItem, UserRankingInfo
from app.services.ranking_service import ranking_service

router = APIRouter()


@router.get("/", response_model=RankingResponse)
def get_rankings(
    period: str = Query(..., description="排行榜周期: day, month, year", enum=["day", "month", "year"]),
    identity: Optional[str] = Query(None, description="身份类型，不传则返回总榜", enum=["student", "office_worker", "flexible", "fitness_pro", "health_care"]),
    target_date: Optional[date] = Query(None, description="目标日期，格式: YYYY-MM-DD，不传则使用今天"),
    limit: int = Query(10, ge=1, le=100, description="返回数量，默认10"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(deps.get_current_active_user)
) -> Any:
    """
    获取排行榜
    - period: 排行榜周期（日榜、月榜、年榜）
    - identity: 身份类型，不传则返回总榜
    - target_date: 目标日期，不传则使用今天
    - limit: 返回数量
    """
    if target_date is None:
        target_date = date.today()
    
    # 获取Top N排行榜
    top_rankings = ranking_service.get_top_rankings(
        period=period,
        limit=limit,
        identity=identity,
        target_date=target_date
    )
    
    # 获取用户信息填充排行榜
    ranking_items = []
    for item in top_rankings:
        user_obj = crud_user.get_user_by_id(db, user_id=item['user_id'])
        if user_obj:
            ranking_items.append(RankingItem(
                user_id=item['user_id'],
                username=user_obj.username,
                calories=item['calories'],
                rank=item['rank'],
                identity=user_obj.identity if hasattr(user_obj, 'identity') else None
            ))
    
    # 获取当前用户排名（如果已登录）
    user_ranking_info = None
    if current_user:
        user_ranking = ranking_service.get_user_ranking(
            user_id=current_user.id,
            period=period,
            identity=identity,
            target_date=target_date
        )
        if user_ranking:
            user_ranking_info = UserRankingInfo(
                user_id=current_user.id,
                rank=user_ranking['rank'],
                calories=user_ranking['calories']
            )
        else:
            user_ranking_info = UserRankingInfo(
                user_id=current_user.id,
                rank=None,
                calories=None
            )
    
    return RankingResponse(
        rankings=ranking_items,
        user_ranking=user_ranking_info,
        period=period,
        identity=identity,
        target_date=target_date
    )


@router.get("/my-ranking", response_model=UserRankingInfo)
def get_my_ranking(
    period: str = Query(..., description="排行榜周期: day, month, year", enum=["day", "month", "year"]),
    identity: Optional[str] = Query(None, description="身份类型，不传则返回总榜", enum=["student", "office_worker", "flexible", "fitness_pro", "health_care"]),
    target_date: Optional[date] = Query(None, description="目标日期，格式: YYYY-MM-DD，不传则使用今天"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    获取当前用户的排名信息
    """
    if target_date is None:
        target_date = date.today()
    
    user_ranking = ranking_service.get_user_ranking(
        user_id=current_user.id,
        period=period,
        identity=identity,
        target_date=target_date
    )
    
    if user_ranking:
        return UserRankingInfo(
            user_id=current_user.id,
            rank=user_ranking['rank'],
            calories=user_ranking['calories']
        )
    else:
        return UserRankingInfo(
            user_id=current_user.id,
            rank=None,
            calories=None
        )
