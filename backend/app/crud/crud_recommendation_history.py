from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Optional

from app.models.recommendation_history import RecommendationHistory
from app.schemas.recommendation_history import RecommendationHistoryCreate


class CRUDRecommendationHistory:
    def create_recommendation_history(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        history_in: RecommendationHistoryCreate
    ) -> RecommendationHistory:
        """创建一条新的推荐调整记录"""
        db_history = RecommendationHistory(
            user_id=user_id,
            adjustment_date=history_in.adjustment_date,
            previous_kcal=history_in.previous_kcal,
            previous_protein_g=history_in.previous_protein_g,
            previous_fat_g=history_in.previous_fat_g,
            previous_carbs_g=history_in.previous_carbs_g,
            new_kcal=history_in.new_kcal,
            new_protein_g=history_in.new_protein_g,
            new_fat_g=history_in.new_fat_g,
            new_carbs_g=history_in.new_carbs_g,
            adjustment_reason=history_in.adjustment_reason,
            trigger_factors=history_in.trigger_factors
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    def get_recommendation_history_by_id(
        self, 
        db: Session, 
        *, 
        history_id: int
    ) -> Optional[RecommendationHistory]:
        """通过ID获取推荐调整记录"""
        return db.query(RecommendationHistory).filter(
            RecommendationHistory.id == history_id
        ).first()

    def get_recommendation_history_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[RecommendationHistory]:
        """获取用户的所有推荐调整记录"""
        return db.query(RecommendationHistory).filter(
            RecommendationHistory.user_id == user_id
        ).order_by(
            RecommendationHistory.adjustment_date.desc()
        ).offset(skip).limit(limit).all()

    def get_recommendation_history_by_user_and_date_range(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        start_date: date, 
        end_date: date
    ) -> List[RecommendationHistory]:
        """获取指定用户和日期范围内的推荐调整记录"""
        return db.query(RecommendationHistory).filter(
            RecommendationHistory.user_id == user_id,
            RecommendationHistory.adjustment_date >= start_date,
            RecommendationHistory.adjustment_date <= end_date
        ).order_by(RecommendationHistory.adjustment_date.desc()).all()

    def get_latest_adjustment(
        self, 
        db: Session, 
        *, 
        user_id: int
    ) -> Optional[RecommendationHistory]:
        """获取用户最新的推荐调整记录"""
        return db.query(RecommendationHistory).filter(
            RecommendationHistory.user_id == user_id
        ).order_by(
            RecommendationHistory.adjustment_date.desc()
        ).first()

    def get_adjustment_count_since(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        since_date: date
    ) -> int:
        """获取自指定日期以来的调整次数"""
        return db.query(RecommendationHistory).filter(
            RecommendationHistory.user_id == user_id,
            RecommendationHistory.adjustment_date >= since_date
        ).count()


# 创建一个实例以便全局使用
recommendation_history = CRUDRecommendationHistory()
