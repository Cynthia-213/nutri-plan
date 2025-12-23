from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.crud.crud_food import food
from app.schemas.food import Food, FoodCreate, FoodPagination
from app.db.session import get_db
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=Food, status_code=status.HTTP_201_CREATED)
def create_food(
    *,
    db: Session = Depends(get_db),
    food_in: FoodCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Create new food item.
    """
    new_food = food.create(db=db, obj_in=food_in)
    return new_food


# 搜索食物
@router.get("/", response_model=FoodPagination)
def search_foods(
    db: Session = Depends(get_db),
    search: str = Query(..., min_length=1, description="搜索关键词"),
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(deps.get_current_active_user)
):
    print(f"Searching foods with keyword: {search}, skip: {skip}, limit: {limit}")
    items = food.search_foods(db, keyword=search, skip=skip, limit=limit)
    total = food.count_foods(db, keyword=search) 
    
    return {"total": total, "items": items}