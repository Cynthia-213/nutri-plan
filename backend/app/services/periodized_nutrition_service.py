"""
周期化营养策略服务
根据训练日/休息日提供差异化的营养推荐
"""
from datetime import date, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.log import CalorieRecommendation
from app.services.calorie_calculator import CalorieCalculatorService
from app.services.calorie_range_calculator import calculate_calorie_range
from app.services.macro_calculator import calculate_all_macros
from app.crud.crud_log import log


class PeriodizedNutritionService:
    """
    周期化营养策略服务
    根据训练日/休息日提供差异化的营养推荐
    """
    
    # 训练日热量调整（相对于基础推荐）
    TRAINING_DAY_ADJUSTMENTS = {
        'lose_weight': {
            'kcal_adjustment': +100,  # 训练日增加100kcal
            'carb_adjustment_pct': +5,  # 碳水比例增加5%
            'protein_adjustment_pct': 0  # 蛋白质比例不变
        },
        'gain_muscle': {
            'kcal_adjustment': +150,  # 训练日增加150kcal
            'carb_adjustment_pct': +8,  # 碳水比例增加8%
            'protein_adjustment_pct': 0
        },
        'body_recomposition': {
            'kcal_adjustment': +100,
            'carb_adjustment_pct': +5,
            'protein_adjustment_pct': 0
        },
        'maintain': {
            'kcal_adjustment': +50,
            'carb_adjustment_pct': +3,
            'protein_adjustment_pct': 0
        },
        'gain_weight': {
            'kcal_adjustment': +100,
            'carb_adjustment_pct': +5,
            'protein_adjustment_pct': 0
        }
    }
    
    # 休息日热量调整
    REST_DAY_ADJUSTMENTS = {
        'lose_weight': {
            'kcal_adjustment': -100,  # 休息日减少100kcal
            'carb_adjustment_pct': -5,  # 碳水比例减少5%
            'protein_adjustment_pct': 0
        },
        'gain_muscle': {
            'kcal_adjustment': -50,  # 休息日减少50kcal
            'carb_adjustment_pct': -5,
            'protein_adjustment_pct': 0
        },
        'body_recomposition': {
            'kcal_adjustment': -100,
            'carb_adjustment_pct': -5,
            'protein_adjustment_pct': 0
        },
        'maintain': {
            'kcal_adjustment': -50,
            'carb_adjustment_pct': -3,
            'protein_adjustment_pct': 0
        },
        'gain_weight': {
            'kcal_adjustment': 0,
            'carb_adjustment_pct': -3,
            'protein_adjustment_pct': 0
        }
    }
    
    def get_periodized_recommendation(
        self,
        user: User,
        target_date: date,
        base_recommendation: CalorieRecommendation,
        db: Optional[Session] = None
    ) -> CalorieRecommendation:
        """
        获取周期化营养推荐（根据训练日/休息日）
        
        :param user: 用户对象
        :param target_date: 目标日期
        :param base_recommendation: 基础推荐
        :param db: 数据库会话（用于检查是否有训练）
        :return: 调整后的推荐
        """
        # 判断是否为训练日
        is_training_day = self._is_training_day(user, target_date, db)
        
        # 获取调整参数
        if is_training_day:
            adjustments = self.TRAINING_DAY_ADJUSTMENTS.get(
                user.goal, 
                self.TRAINING_DAY_ADJUSTMENTS['maintain']
            )
            day_type = '训练日'
        else:
            adjustments = self.REST_DAY_ADJUSTMENTS.get(
                user.goal,
                self.REST_DAY_ADJUSTMENTS['maintain']
            )
            day_type = '休息日'
        
        # 计算调整后的热量
        adjusted_kcal = base_recommendation.recommended_kcal + adjustments['kcal_adjustment']
        
        # 确保不低于最小值
        bmr = CalorieCalculatorService.get_user_bmr(user, prefer_katch_mcardle=True)
        min_kcal = bmr * 1.1
        adjusted_kcal = max(adjusted_kcal, min_kcal)
        
        # 重新计算宏量营养素（考虑碳水调整）
        macros = self._calculate_adjusted_macros(
            user,
            adjusted_kcal,
            base_recommendation,
            adjustments
        )
        
        # 更新区间描述
        range_description = f"{base_recommendation.range_description}（{day_type}调整：{adjustments['kcal_adjustment']:+d}kcal）"
        
        return CalorieRecommendation(
            goal=base_recommendation.goal,
            recommended_kcal=round(adjusted_kcal, 2),
            min_kcal=base_recommendation.min_kcal,
            max_kcal=base_recommendation.max_kcal,
            protein_g=round(macros['protein']['recommended_g'], 2),
            protein_min_g=round(macros['protein']['min_g'], 2),
            protein_max_g=round(macros['protein']['max_g'], 2),
            fat_g=round(macros['fat']['recommended_g'], 2),
            fat_min_g=round(macros['fat']['min_g'], 2),
            fat_max_g=round(macros['fat']['max_g'], 2),
            carbs_g=round(macros['carbs']['recommended_g'], 2),
            range_description=range_description
        )
    
    def _is_training_day(
        self,
        user: User,
        target_date: date,
        db: Optional[Session]
    ) -> bool:
        """
        判断指定日期是否为训练日
        基于运动日志或用户活动水平
        """
        if db:
            # 检查是否有运动记录
            exercise_logs = log.get_exercise_logs_by_user_and_date(
                db,
                user_id=user.id,
                log_date=target_date
            )
            if exercise_logs:
                # 有运动记录，判断为训练日
                total_duration = sum([log_entry.duration_minutes for log_entry in exercise_logs])
                return total_duration >= 20  # 至少20分钟才算训练日
        
        # 如果没有数据库或没有记录，根据活动水平判断
        # 高活动人群默认更多训练日
        if user.activity_level in ['very_active', 'extra_active']:
            # 简单规则：每周5-6天训练日
            day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
            return day_of_week < 6  # 周一到周六为训练日
        elif user.activity_level == 'moderately_active':
            # 每周3-4天训练日
            day_of_week = target_date.weekday()
            return day_of_week < 4  # 周一到周四为训练日
        else:
            # 低活动人群，默认休息日
            return False
    
    def _calculate_adjusted_macros(
        self,
        user: User,
        adjusted_kcal: float,
        base_recommendation: CalorieRecommendation,
        adjustments: Dict
    ) -> Dict:
        """
        计算调整后的宏量营养素
        考虑碳水比例的调整
        """
        from app.services.macro_calculator import calculate_all_macros, CALORIES_PER_GRAM
        
        # 先计算基础宏量营养素
        base_macros = calculate_all_macros(user, adjusted_kcal)
        
        # 调整碳水比例
        carb_adjustment_pct = adjustments.get('carb_adjustment_pct', 0) / 100
        
        # 当前碳水热量
        current_carb_kcal = base_macros['carbs']['recommended_g'] * CALORIES_PER_GRAM['carbs']
        current_carb_pct = current_carb_kcal / adjusted_kcal
        
        # 目标碳水比例
        target_carb_pct = current_carb_pct + carb_adjustment_pct
        target_carb_kcal = adjusted_kcal * target_carb_pct
        target_carb_g = target_carb_kcal / CALORIES_PER_GRAM['carbs']
        
        # 调整脂肪以平衡（保持蛋白质不变）
        protein_kcal = base_macros['protein']['recommended_g'] * CALORIES_PER_GRAM['protein']
        fat_kcal = adjusted_kcal - protein_kcal - target_carb_kcal
        fat_g = fat_kcal / CALORIES_PER_GRAM['fat']
        
        # 确保脂肪不低于最低需求（20%总热量）
        min_fat_kcal = adjusted_kcal * 0.20
        if fat_kcal < min_fat_kcal:
            fat_kcal = min_fat_kcal
            fat_g = fat_kcal / CALORIES_PER_GRAM['fat']
            # 重新调整碳水
            target_carb_kcal = adjusted_kcal - protein_kcal - fat_kcal
            target_carb_g = target_carb_kcal / CALORIES_PER_GRAM['carbs']
        
        return {
            'protein': base_macros['protein'],
            'fat': {
                'recommended_g': round(fat_g, 1),
                'min_g': round(fat_g * 0.9, 1),
                'max_g': round(fat_g * 1.1, 1),
                'percentage': round((fat_kcal / adjusted_kcal) * 100, 1)
            },
            'carbs': {
                'recommended_g': round(target_carb_g, 1),
                'percentage': round((target_carb_kcal / adjusted_kcal) * 100, 1)
            }
        }
    
    def get_weekly_periodized_plan(
        self,
        user: User,
        start_date: date,
        base_recommendation: CalorieRecommendation,
        db: Optional[Session] = None
    ) -> Dict:
        """
        获取一周的周期化营养计划
        
        :param user: 用户对象
        :param start_date: 开始日期（通常是周一）
        :param base_recommendation: 基础推荐
        :param db: 数据库会话
        :return: 包含每天推荐的字典
        """
        weekly_plan = {}
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            day_recommendation = self.get_periodized_recommendation(
                user=user,
                target_date=current_date,
                base_recommendation=base_recommendation,
                db=db
            )
            
            weekly_plan[current_date.isoformat()] = {
                'date': current_date.isoformat(),
                'day_name': current_date.strftime('%A'),
                'is_training_day': self._is_training_day(user, current_date, db),
                'recommendation': day_recommendation
            }
        
        return {
            'start_date': start_date.isoformat(),
            'weekly_plan': weekly_plan,
            'summary': self._generate_weekly_summary(weekly_plan)
        }
    
    def _generate_weekly_summary(self, weekly_plan: Dict) -> Dict:
        """生成周计划摘要"""
        training_days = sum([1 for day in weekly_plan.values() if day['is_training_day']])
        rest_days = 7 - training_days
        
        avg_training_kcal = sum([
            day['recommendation'].recommended_kcal 
            for day in weekly_plan.values() 
            if day['is_training_day']
        ]) / max(training_days, 1)
        
        avg_rest_kcal = sum([
            day['recommendation'].recommended_kcal 
            for day in weekly_plan.values() 
            if not day['is_training_day']
        ]) / max(rest_days, 1)
        
        return {
            'training_days': training_days,
            'rest_days': rest_days,
            'avg_training_day_kcal': round(avg_training_kcal, 0),
            'avg_rest_day_kcal': round(avg_rest_kcal, 0),
            'weekly_total_kcal': round(sum([
                day['recommendation'].recommended_kcal 
                for day in weekly_plan.values()
            ]), 0)
        }


# 创建全局实例
periodized_nutrition_service = PeriodizedNutritionService()
