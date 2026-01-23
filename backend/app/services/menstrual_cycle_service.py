"""
女性月经周期营养调整服务
根据月经周期的不同阶段调整营养推荐
"""
from datetime import date, timedelta
from typing import Dict, Optional
from app.models.user import User
from app.schemas.log import CalorieRecommendation


class MenstrualCycleService:
    """
    女性月经周期营养调整服务
    根据月经周期的不同阶段提供差异化的营养推荐
    """
    
    # 月经周期阶段（通常为28天）
    CYCLE_PHASES = {
        'menstrual': {  # 月经期（第1-5天）
            'days': (1, 5),
            'kcal_adjustment': -50,  # 轻微减少热量
            'carb_adjustment_pct': -2,  # 略微减少碳水
            'protein_adjustment_pct': 0,
            'description': '月经期：能量需求略低，建议增加铁质摄入'
        },
        'follicular': {  # 卵泡期（第6-14天）
            'days': (6, 14),
            'kcal_adjustment': 0,  # 正常热量
            'carb_adjustment_pct': 0,
            'protein_adjustment_pct': 0,
            'description': '卵泡期：代谢率正常，适合正常训练和营养'
        },
        'ovulation': {  # 排卵期（第15-17天）
            'days': (15, 17),
            'kcal_adjustment': +50,  # 轻微增加热量
            'carb_adjustment_pct': +2,  # 略微增加碳水
            'protein_adjustment_pct': 0,
            'description': '排卵期：代谢率略高，能量需求增加'
        },
        'luteal': {  # 黄体期（第18-28天）
            'days': (18, 28),
            'kcal_adjustment': +100,  # 增加热量（应对PMS和食欲增加）
            'carb_adjustment_pct': +3,  # 增加碳水（稳定血糖）
            'protein_adjustment_pct': 0,
            'description': '黄体期：代谢率提高，食欲可能增加，建议增加热量和碳水'
        }
    }
    
    def get_cycle_phase(
        self,
        user: User,
        target_date: date,
        last_period_start: Optional[date] = None
    ) -> Dict:
        """
        获取指定日期的月经周期阶段
        
        :param user: 用户对象（必须是女性）
        :param target_date: 目标日期
        :param last_period_start: 上次月经开始日期（如果提供）
        :return: 包含阶段信息的字典
        """
        if user.gender != 'female':
            return {
                'phase': None,
                'message': '仅适用于女性用户'
            }
        
        # 如果没有提供上次月经日期，返回默认值
        if not last_period_start:
            return {
                'phase': 'unknown',
                'message': '需要记录月经周期信息',
                'suggestion': '建议记录上次月经开始日期以获得个性化调整'
            }
        
        # 计算距离上次月经的天数
        days_since_period = (target_date - last_period_start).days
        
        # 处理周期超过28天的情况（取模）
        cycle_day = (days_since_period % 28) + 1
        
        # 确定当前阶段
        if 1 <= cycle_day <= 5:
            phase = 'menstrual'
        elif 6 <= cycle_day <= 14:
            phase = 'follicular'
        elif 15 <= cycle_day <= 17:
            phase = 'ovulation'
        else:  # 18-28
            phase = 'luteal'
        
        phase_info = self.CYCLE_PHASES[phase]
        
        return {
            'phase': phase,
            'cycle_day': cycle_day,
            'days_since_period': days_since_period,
            'adjustments': {
                'kcal_adjustment': phase_info['kcal_adjustment'],
                'carb_adjustment_pct': phase_info['carb_adjustment_pct'],
                'protein_adjustment_pct': phase_info['protein_adjustment_pct']
            },
            'description': phase_info['description']
        }
    
    def adjust_recommendation_for_cycle(
        self,
        user: User,
        target_date: date,
        base_recommendation: CalorieRecommendation,
        last_period_start: Optional[date] = None
    ) -> CalorieRecommendation:
        """
        根据月经周期调整推荐
        
        :param user: 用户对象
        :param target_date: 目标日期
        :param base_recommendation: 基础推荐
        :param last_period_start: 上次月经开始日期
        :return: 调整后的推荐
        """
        if user.gender != 'female':
            return base_recommendation
        
        cycle_info = self.get_cycle_phase(user, target_date, last_period_start)
        
        if cycle_info['phase'] in [None, 'unknown']:
            return base_recommendation
        
        adjustments = cycle_info['adjustments']
        
        # 计算调整后的热量
        adjusted_kcal = base_recommendation.recommended_kcal + adjustments['kcal_adjustment']
        
        # 确保不低于最小值
        from app.services.calorie_calculator import CalorieCalculatorService
        bmr = CalorieCalculatorService.get_user_bmr(user, prefer_katch_mcardle=True)
        min_kcal = bmr * 1.1
        adjusted_kcal = max(adjusted_kcal, min_kcal)
        
        # 调整宏量营养素
        adjusted_macros = self._adjust_macros_for_cycle(
            base_recommendation,
            adjusted_kcal,
            adjustments
        )
        
        # 更新描述
        range_description = f"{base_recommendation.range_description}（{cycle_info['description']}）"
        
        return CalorieRecommendation(
            goal=base_recommendation.goal,
            recommended_kcal=round(adjusted_kcal, 2),
            min_kcal=base_recommendation.min_kcal,
            max_kcal=base_recommendation.max_kcal,
            protein_g=round(adjusted_macros['protein_g'], 2),
            protein_min_g=round(adjusted_macros.get('protein_min_g', adjusted_macros['protein_g'] * 0.9), 2),
            protein_max_g=round(adjusted_macros.get('protein_max_g', adjusted_macros['protein_g'] * 1.1), 2),
            fat_g=round(adjusted_macros['fat_g'], 2),
            fat_min_g=round(adjusted_macros.get('fat_min_g', adjusted_macros['fat_g'] * 0.9), 2),
            fat_max_g=round(adjusted_macros.get('fat_max_g', adjusted_macros['fat_g'] * 1.1), 2),
            carbs_g=round(adjusted_macros['carbs_g'], 2),
            range_description=range_description
        )
    
    def _adjust_macros_for_cycle(
        self,
        base_recommendation: CalorieRecommendation,
        adjusted_kcal: float,
        adjustments: Dict
    ) -> Dict:
        """调整宏量营养素以适应周期变化"""
        from app.services.macro_calculator import CALORIES_PER_GRAM
        
        # 蛋白质保持不变
        protein_g = base_recommendation.protein_g
        
        # 调整碳水比例
        carb_adjustment_pct = adjustments.get('carb_adjustment_pct', 0) / 100
        
        # 当前碳水热量和比例
        current_carb_kcal = base_recommendation.carbs_g * CALORIES_PER_GRAM['carbs']
        current_carb_pct = current_carb_kcal / base_recommendation.recommended_kcal if base_recommendation.recommended_kcal > 0 else 0.4
        
        # 目标碳水比例
        target_carb_pct = current_carb_pct + carb_adjustment_pct
        target_carb_kcal = adjusted_kcal * target_carb_pct
        carbs_g = target_carb_kcal / CALORIES_PER_GRAM['carbs']
        
        # 计算脂肪（剩余热量）
        protein_kcal = protein_g * CALORIES_PER_GRAM['protein']
        fat_kcal = adjusted_kcal - protein_kcal - target_carb_kcal
        fat_g = fat_kcal / CALORIES_PER_GRAM['fat']
        
        # 确保脂肪不低于最低需求（20%总热量）
        min_fat_kcal = adjusted_kcal * 0.20
        if fat_kcal < min_fat_kcal:
            fat_kcal = min_fat_kcal
            fat_g = fat_kcal / CALORIES_PER_GRAM['fat']
            # 重新调整碳水
            target_carb_kcal = adjusted_kcal - protein_kcal - fat_kcal
            carbs_g = target_carb_kcal / CALORIES_PER_GRAM['carbs']
        
        return {
            'protein_g': protein_g,
            'fat_g': fat_g,
            'carbs_g': carbs_g
        }


# 创建全局实例
menstrual_cycle_service = MenstrualCycleService()
