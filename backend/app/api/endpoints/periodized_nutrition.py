from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.services.recommendation_service import RecommendationService
from app.services.periodized_nutrition_service import periodized_nutrition_service
from app.services.menstrual_cycle_service import menstrual_cycle_service

router = APIRouter()


@router.get("/daily", summary="获取指定日期的周期化营养推荐")
def get_daily_periodized_recommendation(
    target_date: Optional[date] = Query(None, description="目标日期，默认为今天"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    获取指定日期的周期化营养推荐
    结合训练日/休息日和女性月经周期调整
    """
    if not target_date:
        target_date = date.today()
    
    # 获取基础推荐
    base_recommendation = RecommendationService.get_calorie_recommendation(
        user=current_user,
        db=db,
        enable_auto_adjustment=True,
        target_date=target_date,
        enable_periodized=True
    )
    
    return {
        'date': target_date.isoformat(),
        'is_training_day': periodized_nutrition_service._is_training_day(
            current_user, target_date, db
        ),
        'cycle_info': (
            menstrual_cycle_service.get_cycle_phase(
                current_user, 
                target_date, 
                current_user.last_period_start if hasattr(current_user, 'last_period_start') else None
            ) if current_user.gender == 'female' else None
        ),
        'recommendation': base_recommendation
    }


@router.get("/weekly", summary="获取一周的周期化营养计划")
def get_weekly_periodized_plan(
    start_date: Optional[date] = Query(None, description="开始日期（通常是周一），默认为本周一"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    获取一周的周期化营养计划
    包含每天的训练日/休息日状态和推荐值
    """
    if not start_date:
        # 计算本周一
        today = date.today()
        days_since_monday = today.weekday()
        start_date = today - timedelta(days=days_since_monday)
    
    # 获取基础推荐
    base_recommendation = RecommendationService.get_calorie_recommendation(
        user=current_user,
        db=db,
        enable_auto_adjustment=True,
        enable_periodized=True
    )
    
    # 获取周计划
    weekly_plan = periodized_nutrition_service.get_weekly_periodized_plan(
        user=current_user,
        start_date=start_date,
        base_recommendation=base_recommendation,
        db=db
    )
    
    return weekly_plan


@router.get("/cycle-info", summary="获取月经周期信息（仅女性）")
def get_menstrual_cycle_info(
    target_date: Optional[date] = Query(None, description="目标日期，默认为今天"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    获取女性用户的月经周期信息
    包括当前阶段和营养调整建议
    """
    if current_user.gender != 'female':
        return {
            'message': '此功能仅适用于女性用户'
        }
    
    if not target_date:
        target_date = date.today()
    
    cycle_info = menstrual_cycle_service.get_cycle_phase(
        user=current_user,
        target_date=target_date,
        last_period_start=current_user.last_period_start if hasattr(current_user, 'last_period_start') else None
    )
    
    return {
        'date': target_date.isoformat(),
        'cycle_info': cycle_info
    }
