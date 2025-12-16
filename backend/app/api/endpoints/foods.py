from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.crud.crud_food import food_crud
from app.schemas.food import Food
from app.db.session import get_db
from app.models.user import User

router = APIRouter()

# 搜索食物
@router.get("/", response_model=List[Food])
def search_foods(
    db: Session = Depends(get_db),
    search: str = Query(..., min_length=1, description="The food keyword to search for"),
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(deps.get_current_active_user)
):
    foods = food_crud.search_foods(db, keyword=search, skip=skip, limit=limit)
    return foods