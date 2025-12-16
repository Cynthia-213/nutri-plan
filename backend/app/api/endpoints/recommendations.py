from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.services.recommendation_service import RecommendationService
from app.services.menu_generator import menu_generator

router = APIRouter()

@router.get("/", summary="Generate AI menu recommendations")
def generate_ai_menu(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    生成基于AI的每日饮食推荐菜单
    """
    if not all([current_user.weight_kg, current_user.height_cm, current_user.birthdate, current_user.gender]):
         raise HTTPException(
            status_code=400,
            detail="Cannot generate menu, your profile is incomplete. Please fill in your height, weight, birthdate, and gender on the profile page.",
        )

    recommendations = RecommendationService.get_calorie_recommendation(current_user)
    
    if recommendations.recommended_kcal == 0:
        raise HTTPException(
            status_code=400,
            detail="Could not calculate your daily recommended intake. Please check your profile information for accuracy.",
        )
        
    generated_menu = menu_generator.generate_menu(
        target_calories=recommendations.recommended_kcal,
        target_protein=recommendations.protein_g,
        target_fat=recommendations.fat_g,
        target_carbs=recommendations.carbs_g,
    )
    
    return generated_menu