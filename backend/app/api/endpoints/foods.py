from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.crud.crud_food import food
from app.crud.crud_banned_food import banned_food
from app.schemas.food import Food, FoodCreate, FoodPagination, BannedFoodCreate, BannedFood, BannedFoodList
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


# 禁止食物相关端点
@router.post("/banned", response_model=BannedFood, status_code=status.HTTP_201_CREATED)
def add_banned_food(
    *,
    db: Session = Depends(get_db),
    banned_food_in: BannedFoodCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    添加禁止的食物
    """
    result = banned_food.create(db=db, user_id=current_user.id, banned_food_in=banned_food_in)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="食物不存在或已被禁止"
        )
    # 加载关联的食物信息
    db.refresh(result)
    return result


@router.get("/banned", response_model=BannedFoodList)
def get_banned_foods(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    获取当前用户的所有禁止食物
    """
    items = banned_food.get_by_user(db, user_id=current_user.id)
    return {"items": items, "total": len(items)}


@router.delete("/banned/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_banned_food(
    *,
    db: Session = Depends(get_db),
    food_id: int,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    删除禁止的食物
    """
    success = banned_food.delete(db=db, user_id=current_user.id, food_id=food_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该禁止食物记录"
        )
    return None