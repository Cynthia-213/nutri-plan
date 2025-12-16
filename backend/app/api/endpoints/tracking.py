from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Any


from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.crud.crud_log import log_crud
from app.crud.crud_food import food_crud
from app.schemas import log as log_schema
from app.services.tracking_service import tracking_service

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
    food = food_crud.get_food_by_id(db, food_id=log_in.food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found.")
        
    food_log = log_crud.create_food_log(db, user_id=current_user.id, log_in=log_in)
    return food_log

@router.post("/exercise-log/", response_model=log_schema.ExerciseLogInDB, status_code=status.HTTP_201_CREATED)
def log_exercise_activity(
    *,
    db: Session = Depends(get_db),
    log_in: log_schema.ExerciseLogCreate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    记录运动活动
    """
    exercise = food_crud.get_exercise_by_id(db, exercise_id=log_in.exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found.")

    exercise_log = log_crud.create_exercise_log(db, user_id=current_user.id, log_in=log_in)
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

    

    

    @router.get("/energy-summary/", response_model=log_schema.EnergySummary)

    def get_energy_summary(

        period_type: str = Query("daily", enum=["daily", "monthly", "yearly"]),

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

    