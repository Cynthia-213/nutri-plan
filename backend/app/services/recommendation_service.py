import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.calorie_calculator import CalorieCalculatorService
from app.services.calorie_range_calculator import calculate_calorie_range
from app.services.macro_calculator import calculate_all_macros
from app.services.dynamic_adjustment_service import dynamic_adjustment_service
from app.services.periodized_nutrition_service import periodized_nutrition_service
from app.services.menstrual_cycle_service import menstrual_cycle_service
from app.schemas.log import CalorieRecommendation
from datetime import date


class RecommendationService:
    """
    提供饮食和营养建议的服务
    支持热量区间和基于科学共识的宏量营养素分配
    支持基于历史数据的自动调整
    """
    @staticmethod
    def get_calorie_recommendation(
        user: User, 
        db: Optional[Session] = None,
        enable_auto_adjustment: bool = True,
        target_date: Optional[date] = None,
        enable_periodized: Optional[bool] = None
    ) -> CalorieRecommendation:
        """
        根据用户的目标，计算推荐的每日热量区间和三大营养素摄入量
        使用新的动态计算逻辑，支持热量区间和人群差异化
        如果启用自动调整，会根据历史数据自动优化推荐
        支持周期化营养（训练日/休息日）和女性月经周期调整
        
        :param user: 用户对象
        :param db: 数据库会话（用于自动调整，可选）
        :param enable_auto_adjustment: 是否启用自动调整（默认True）
        :param target_date: 目标日期（用于周期化营养，默认今天）
        :param enable_periodized: 是否启用周期化营养（默认根据用户设置）
        :return: 一个包含推荐值和区间的 Pydantic 模型
        """
        # 1. 计算用户的TDEE (总日能量消耗)
        # 如果有体脂率数据，优先使用Katch-McArdle公式
        tdee = CalorieCalculatorService.get_user_tdee(user, prefer_katch_mcardle=True)
        if tdee == 0:
            # 如果无法计算TDEE（信息不全），返回一个空/默认的推荐
            logging.warning(f"Unable to calculate TDEE for user {user.id}. Incomplete profile data.")
            return CalorieRecommendation(
                goal=user.goal,
                recommended_kcal=0,
                protein_g=0,
                fat_g=0,
                carbs_g=0
            )

        # 2. 计算热量区间
        calorie_range = calculate_calorie_range(user, tdee)
        recommended_kcal = calorie_range['recommended_kcal']
        min_kcal = calorie_range['min_kcal']
        max_kcal = calorie_range['max_kcal']
        range_description = calorie_range['range_description']

        # 3. 计算宏量营养素
        macros = calculate_all_macros(user, recommended_kcal)
        
        protein = macros['protein']
        fat = macros['fat']
        carbs = macros['carbs']

        base_recommendation = CalorieRecommendation(
            goal=user.goal.replace('_', ' ').title(),
            recommended_kcal=round(recommended_kcal, 2),
            min_kcal=round(min_kcal, 2),
            max_kcal=round(max_kcal, 2),
            protein_g=round(protein['recommended_g'], 2),
            protein_min_g=round(protein['min_g'], 2),
            protein_max_g=round(protein['max_g'], 2),
            fat_g=round(fat['recommended_g'], 2),
            fat_min_g=round(fat['min_g'], 2),
            fat_max_g=round(fat['max_g'], 2),
            carbs_g=round(carbs['recommended_g'], 2),
            range_description=range_description
        )
        
        # 如果启用自动调整且有数据库会话，尝试自动调整
        if enable_auto_adjustment and db:
            try:
                adjusted_recommendation = dynamic_adjustment_service.evaluate_and_adjust(
                    user=user,
                    db=db,
                    current_recommendation=base_recommendation
                )
                base_recommendation = adjusted_recommendation
            except Exception as e:
                logging.warning(f"Auto adjustment failed for user {user.id}: {e}")
        
        # 周期化营养调整（训练日/休息日）
        target_date = target_date or date.today()
        enable_periodized = enable_periodized if enable_periodized is not None else (
            user.enable_periodized_nutrition == 'true' if hasattr(user, 'enable_periodized_nutrition') else False
        )
        
        if enable_periodized and db:
            try:
                periodized_recommendation = periodized_nutrition_service.get_periodized_recommendation(
                    user=user,
                    target_date=target_date,
                    base_recommendation=base_recommendation,
                    db=db
                )
                base_recommendation = periodized_recommendation
            except Exception as e:
                logging.warning(f"Periodized nutrition adjustment failed for user {user.id}: {e}")
        
        # 女性月经周期调整
        if user.gender == 'female' and hasattr(user, 'last_period_start') and user.last_period_start:
            try:
                cycle_adjusted = menstrual_cycle_service.adjust_recommendation_for_cycle(
                    user=user,
                    target_date=target_date,
                    base_recommendation=base_recommendation,
                    last_period_start=user.last_period_start
                )
                base_recommendation = cycle_adjusted
            except Exception as e:
                logging.warning(f"Menstrual cycle adjustment failed for user {user.id}: {e}")
        
        return base_recommendation