from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.exercise import Exercise

class CRUDExercise:
    def get_exercise_by_id(self, db: Session, *, exercise_id: int) -> Optional[Exercise]:
        """通过ID获取运动项目"""
        return db.query(Exercise).filter(Exercise.id == exercise_id).first()
    def list_exercises(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Exercise]:
        """列出所有运动项目"""
        return db.query(Exercise).offset(skip).limit(limit).all()

# 创建一个实例以便全局使用
exercise = CRUDExercise()
