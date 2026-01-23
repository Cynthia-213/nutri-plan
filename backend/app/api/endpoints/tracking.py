from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Any


from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.crud.crud_log import log
from app.crud.crud_food import food
from app.crud.crud_exercise import exercise
from app.schemas import log as log_schema
from app.services.tracking_service import tracking_service
from app.services.ranking_service import ranking_service

router = APIRouter()

@router.post("/food-log/", response_model=log_schema.FoodLogInDB, status_code=status.HTTP_201_CREATED)
def log_food_intake(
    *,
    db: Session = Depends(get_db),
    log_in: log_schema.FoodLogCreate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    记录饮食摄入
    """
    cur_food = food.get_food_by_id(db, food_id=log_in.food_id)
    if not cur_food:
        raise HTTPException(status_code=404, detail="Food not found.")
        
    food_log = log.create_food_log(db, user_id=current_user.id, log_in=log_in)
    return food_log

@router.post("/exercise-log/", response_model=log_schema.ExerciseLogInDB, status_code=status.HTTP_201_CREATED)
def log_exercise_activity(
    *,
    db: Session = Depends(get_db),
    log_in: log_schema.ExerciseLogCreate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    记录运动活动，并实时更新排行榜
    """
    cur_exercise = exercise.get_exercise_by_id(db, exercise_id=log_in.exercise_id)
    if not cur_exercise:
        raise HTTPException(status_code=404, detail="Exercise not found.")

    exercise_log = log.create_exercise_log(db, user_id=current_user.id, log_in=log_in)
    
    # 实时更新排行榜
    try:
        calories = float(exercise_log.calories_burned)
        user_identity = current_user.identity if hasattr(current_user, 'identity') else 'office_worker'
        ranking_service.update_ranking(
            user_id=current_user.id,
            calories=calories,
            user_identity=user_identity,
            log_date=log_in.log_date
        )
    except Exception as e:
        # 排行榜更新失败不应该影响运动记录的正常创建
        # 可以记录日志，但不抛出异常
        print(f"Failed to update ranking: {e}")
    
    return exercise_log


@router.get("/daily-summary/", response_model=log_schema.DailySummary)
def get_daily_summary(
    date: date = Query(..., description="The date for the summary, in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    每日总结
    """
    if not all([current_user.weight_kg, current_user.height_cm, current_user.birthdate, current_user.gender]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile is incomplete. Please provide height, weight, birthdate, and gender to get a summary.",
        )

    daliy_summary = tracking_service.get_daily_summary(db, user=current_user, log_date=date)

    return daliy_summary


@router.post("/ai-summary/", response_model=dict)
def generate_ai_summary(
    date: date = Query(..., description="The date for AI analysis, in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    生成AI健康建议（独立接口）
    """
    if not all([current_user.weight_kg, current_user.height_cm, current_user.birthdate, current_user.gender]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile is incomplete. Please provide height, weight, birthdate, and gender to get AI analysis.",
        )

    ai_summary = tracking_service.generate_ai_summary(db, user=current_user, log_date=date)
    
    return {"ai_summary": ai_summary}

    
@router.get("/energy-summary/", response_model=log_schema.EnergySummary)
def get_energy_summary(
    period_type: str = Query("daily", enum=["daily", "monthly"]),
    energy_type: str = Query("intake", enum=["intake", "expenditure"]),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    获取能量总结
    """
    summary = tracking_service.get_energy_summary(
        db, 
        user=current_user, 
        period_type=period_type, 
        energy_type=energy_type, 
        start_date=start_date, 
        end_date=end_date
    )
    return summary