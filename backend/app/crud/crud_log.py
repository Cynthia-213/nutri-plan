from sqlalchemy.orm import Session, joinedload
from datetime import date
from typing import List

from app.models.log import UserFoodLog, UserExerciseLog
from app.schemas.log import FoodLogCreate, ExerciseLogCreate

class CRUDLog:
    def create_food_log(self, db: Session, *, user_id: int, log_in: FoodLogCreate) -> UserFoodLog:
        """创建一条新的饮食记录"""
        db_log = UserFoodLog(
            user_id=user_id,
            food_id=log_in.food_id,
            serving_grams=log_in.serving_grams,
            log_date=log_in.log_date
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

    def get_food_logs_by_user_and_date(self, db: Session, *, user_id: int, log_date: date) -> List[UserFoodLog]:
        """获取指定用户和日期的所有饮食记录，并预加载食物信息"""
        return db.query(UserFoodLog).options(joinedload(UserFoodLog.food)).filter(
            UserFoodLog.user_id == user_id, 
            UserFoodLog.log_date == log_date
        ).all()

    def get_food_logs_by_user_and_date_range(self, db: Session, *, user_id: int, start_date: date, end_date: date) -> List[UserFoodLog]:
        """获取指定用户和日期范围内的所有饮食记录，并预加载食物信息"""
        return db.query(UserFoodLog).options(joinedload(UserFoodLog.food)).filter(
            UserFoodLog.user_id == user_id,
            UserFoodLog.log_date >= start_date,
            UserFoodLog.log_date <= end_date
        ).all()

    def create_exercise_log(self, db: Session, *, user_id: int, log_in: ExerciseLogCreate) -> UserExerciseLog:
        """创建一条新的运动记录"""
        db_log = UserExerciseLog(
            user_id=user_id,
            exercise_id=log_in.exercise_id,
            duration_minutes=log_in.duration_minutes,
            calories_burned=log_in.calories_burned,
            log_date=log_in.log_date
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

    def get_exercise_logs_by_user_and_date(self, db: Session, *, user_id: int, log_date: date) -> List[UserExerciseLog]:
        """获取指定用户和日期的所有运动记录，并预加载运动信息"""
        return db.query(UserExerciseLog).options(joinedload(UserExerciseLog.exercise)).filter(
            UserExerciseLog.user_id == user_id, 
            UserExerciseLog.log_date == log_date
        ).all()

    def get_exercise_logs_by_user_and_date_range(self, db: Session, *, user_id: int, start_date: date, end_date: date) -> List[UserExerciseLog]:
        """获取指定用户和日期范围内的所有运动记录，并预加载运动信息"""
        return db.query(UserExerciseLog).options(joinedload(UserExerciseLog.exercise)).filter(
            UserExerciseLog.user_id == user_id,
            UserExerciseLog.log_date >= start_date,
            UserExerciseLog.log_date <= end_date
        ).all()

# 创建一个实例以便全局使用
log = CRUDLog()