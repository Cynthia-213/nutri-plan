from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.services.performance_analysis_service import performance_analysis_service

router = APIRouter()


@router.get("/analysis", summary="获取训练表现分析")
def get_performance_analysis(
    weeks: int = Query(4, ge=1, le=12, description="分析的时间范围（周）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    获取用户的训练表现分析
    包括总体趋势、力量训练趋势、有氧训练趋势、训练频率和强度分析
    """
    analysis = performance_analysis_service.analyze_training_performance(
        user=current_user,
        db=db,
        weeks=weeks
    )
    
    return analysis
