from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.crud.crud_food import food_crud
from app.schemas.exercise import Exercise
from app.db.session import get_db
from app.models.user import User

router = APIRouter()

# 获取运动列表
@router.get("/", response_model=List[Exercise])
def list_all_exercises(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(deps.get_current_active_user)
):
    exercises = food_crud.list_exercises(db, skip=skip, limit=limit)
    return exercises