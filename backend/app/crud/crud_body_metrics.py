from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Optional, Tuple
from decimal import Decimal

from app.models.body_metrics import BodyMetrics
from app.schemas.body_metrics import BodyMetricsCreate, BodyMetricsUpdate


class CRUDBodyMetrics:
    def create_body_metrics(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        metrics_in: BodyMetricsCreate
    ) -> BodyMetrics:
        """创建一条新的身体指标记录"""
        db_metrics = BodyMetrics(
            user_id=user_id,
            record_date=metrics_in.record_date,
            weight_kg=metrics_in.weight_kg,
            body_fat_pct=metrics_in.body_fat_pct,
            muscle_mass_kg=metrics_in.muscle_mass_kg,
            notes=metrics_in.notes
        )
        db.add(db_metrics)
        db.commit()
        db.refresh(db_metrics)
        return db_metrics

    def get_body_metrics_by_id(
        self, 
        db: Session, 
        *, 
        metrics_id: int
    ) -> Optional[BodyMetrics]:
        """通过ID获取身体指标记录"""
        return db.query(BodyMetrics).filter(BodyMetrics.id == metrics_id).first()

    def get_body_metrics_by_user_and_date(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        record_date: date
    ) -> Optional[BodyMetrics]:
        """获取指定用户和日期的身体指标记录"""
        return db.query(BodyMetrics).filter(
            BodyMetrics.user_id == user_id,
            BodyMetrics.record_date == record_date
        ).first()

    def get_body_metrics_by_user_and_date_range(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        start_date: date, 
        end_date: date
    ) -> List[BodyMetrics]:
        """获取指定用户和日期范围内的所有身体指标记录"""
        return db.query(BodyMetrics).filter(
            BodyMetrics.user_id == user_id,
            BodyMetrics.record_date >= start_date,
            BodyMetrics.record_date <= end_date
        ).order_by(BodyMetrics.record_date.asc()).all()

    def get_weight_history(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        weeks: int = 8
    ) -> List[Tuple[date, float]]:
        """
        获取体重历史记录（最近N周）
        返回: [(date, weight_kg), ...]
        """
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks)
        
        metrics = self.get_body_metrics_by_user_and_date_range(
            db, 
            user_id=user_id, 
            start_date=start_date, 
            end_date=end_date
        )
        
        # 只返回有体重数据的记录
        history = []
        for m in metrics:
            if m.weight_kg:
                history.append((m.record_date, float(m.weight_kg)))
        
        return history

    def get_body_fat_history(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        weeks: int = 8
    ) -> List[Tuple[date, float]]:
        """
        获取体脂率历史记录（最近N周）
        返回: [(date, body_fat_pct), ...]
        """
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks)
        
        metrics = self.get_body_metrics_by_user_and_date_range(
            db, 
            user_id=user_id, 
            start_date=start_date, 
            end_date=end_date
        )
        
        # 只返回有体脂率数据的记录
        history = []
        for m in metrics:
            if m.body_fat_pct:
                history.append((m.record_date, float(m.body_fat_pct)))
        
        return history

    def get_latest_body_metrics(
        self, 
        db: Session, 
        *, 
        user_id: int
    ) -> Optional[BodyMetrics]:
        """获取用户最新的身体指标记录"""
        return db.query(BodyMetrics).filter(
            BodyMetrics.user_id == user_id
        ).order_by(BodyMetrics.record_date.desc()).first()

    def update_body_metrics(
        self, 
        db: Session, 
        *, 
        db_metrics: BodyMetrics, 
        metrics_in: BodyMetricsUpdate
    ) -> BodyMetrics:
        """更新身体指标记录"""
        update_data = metrics_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_metrics, field, value)
        
        db.add(db_metrics)
        db.commit()
        db.refresh(db_metrics)
        return db_metrics

    def delete_body_metrics(
        self, 
        db: Session, 
        *, 
        metrics_id: int
    ) -> bool:
        """删除身体指标记录"""
        db_metrics = self.get_body_metrics_by_id(db, metrics_id=metrics_id)
        if db_metrics:
            db.delete(db_metrics)
            db.commit()
            return True
        return False


# 创建一个实例以便全局使用
body_metrics = CRUDBodyMetrics()
