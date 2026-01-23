from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.crud.crud_body_metrics import body_metrics
from app.schemas.body_metrics import (
    BodyMetricsCreate,
    BodyMetricsUpdate,
    BodyMetricsInDB,
    BodyMetricsTrendResponse
)

router = APIRouter()


@router.post("/", response_model=BodyMetricsInDB, summary="记录身体指标")
def create_body_metrics(
    metrics_in: BodyMetricsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    记录用户的身体指标（体重、体脂率等）
    """
    # 检查是否已存在该日期的记录
    existing = body_metrics.get_body_metrics_by_user_and_date(
        db, 
        user_id=current_user.id, 
        record_date=metrics_in.record_date
    )
    
    if existing:
        # 如果已存在，更新记录
        updated = body_metrics.update_body_metrics(
            db, 
            db_metrics=existing, 
            metrics_in=BodyMetricsUpdate(**metrics_in.model_dump())
        )
        return updated
    
    # 创建新记录
    return body_metrics.create_body_metrics(
        db, 
        user_id=current_user.id, 
        metrics_in=metrics_in
    )


@router.get("/", response_model=List[BodyMetricsInDB], summary="获取身体指标历史")
def get_body_metrics_history(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    获取用户的身体指标历史记录
    如果不指定日期范围，默认返回最近8周的数据
    """
    if not start_date:
        end_date = end_date or date.today()
        start_date = end_date - timedelta(weeks=8)
    else:
        end_date = end_date or date.today()
    
    return body_metrics.get_body_metrics_by_user_and_date_range(
        db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/trends", response_model=BodyMetricsTrendResponse, summary="获取身体指标趋势")
def get_body_metrics_trends(
    weeks: int = 8,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    获取用户的身体指标趋势分析
    返回包含体重和体脂率变化的数据
    """
    from app.schemas.body_metrics import BodyMetricsTrend
    
    end_date = date.today()
    start_date = end_date - timedelta(weeks=weeks)
    
    metrics_list = body_metrics.get_body_metrics_by_user_and_date_range(
        db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    trends = []
    prev_weight = None
    prev_bf = None
    
    for m in metrics_list:
        weight_change = None
        bf_change = None
        
        if m.weight_kg:
            weight_kg = float(m.weight_kg)
            if prev_weight is not None:
                weight_change = weight_kg - prev_weight
            prev_weight = weight_kg
        else:
            weight_kg = None
        
        if m.body_fat_pct:
            bf_pct = float(m.body_fat_pct)
            if prev_bf is not None:
                bf_change = bf_pct - prev_bf
            prev_bf = bf_pct
        else:
            bf_pct = None
        
        trends.append(BodyMetricsTrend(
            record_date=m.record_date,
            weight_kg=weight_kg,
            body_fat_pct=bf_pct,
            weight_change_kg=weight_change,
            body_fat_change_pct=bf_change
        ))
    
    return BodyMetricsTrendResponse(
        data=trends,
        total_records=len(trends)
    )


@router.get("/latest", response_model=BodyMetricsInDB, summary="获取最新身体指标")
def get_latest_body_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    获取用户最新的身体指标记录
    """
    latest = body_metrics.get_latest_body_metrics(db, user_id=current_user.id)
    if not latest:
        raise HTTPException(status_code=404, detail="未找到身体指标记录")
    return latest


@router.put("/{metrics_id}", response_model=BodyMetricsInDB, summary="更新身体指标")
def update_body_metrics(
    metrics_id: int,
    metrics_in: BodyMetricsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    更新指定的身体指标记录
    """
    db_metrics = body_metrics.get_body_metrics_by_id(db, metrics_id=metrics_id)
    if not db_metrics:
        raise HTTPException(status_code=404, detail="未找到该记录")
    
    if db_metrics.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该记录")
    
    return body_metrics.update_body_metrics(
        db, 
        db_metrics=db_metrics, 
        metrics_in=metrics_in
    )


@router.delete("/{metrics_id}", summary="删除身体指标")
def delete_body_metrics(
    metrics_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    删除指定的身体指标记录
    """
    db_metrics = body_metrics.get_body_metrics_by_id(db, metrics_id=metrics_id)
    if not db_metrics:
        raise HTTPException(status_code=404, detail="未找到该记录")
    
    if db_metrics.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该记录")
    
    success = body_metrics.delete_body_metrics(db, metrics_id=metrics_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除失败")
    
    return {"message": "删除成功"}
