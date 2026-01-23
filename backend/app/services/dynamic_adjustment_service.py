"""
动态调整服务
基于用户历史数据（体重、体脂率、执行情况）自动调整营养推荐
"""
import logging
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.log import CalorieRecommendation
from app.services.calorie_calculator import CalorieCalculatorService
from app.services.calorie_range_calculator import calculate_calorie_range
from app.services.macro_calculator import calculate_all_macros
from app.crud.crud_body_metrics import body_metrics
from app.crud.crud_log import log
from app.crud.crud_recommendation_history import recommendation_history
from app.services.performance_analysis_service import performance_analysis_service


class DynamicAdjustmentService:
    """
    动态调整引擎
    评估用户数据并决定是否需要调整推荐
    """
    
    def __init__(self):
        self.min_adjustment_interval_days = 14  # 最小调整间隔（天）
        self.max_adjustment_kcal = 200  # 最大单次调整幅度（kcal）
        self.min_kcal_multiplier = 1.1  # 最低热量 = BMR × 1.1
    
    def evaluate_and_adjust(
        self,
        user: User,
        db: Session,
        current_recommendation: CalorieRecommendation
    ) -> CalorieRecommendation:
        """
        评估当前推荐并决定是否调整
        
        :param user: 用户对象
        :param db: 数据库会话
        :param current_recommendation: 当前推荐
        :return: 调整后的推荐（如果不需要调整则返回原推荐）
        """
        # 1. 检查是否满足调整条件（时间间隔）
        if not self._can_adjust(db, user.id):
            return current_recommendation
        
        # 2. 收集历史数据
        weight_history = body_metrics.get_weight_history(db, user_id=user.id, weeks=8)
        body_fat_history = body_metrics.get_body_fat_history(db, user_id=user.id, weeks=8)
        daily_logs = self._get_daily_logs(db, user.id, days=14)
        
        # 3. 多维度评估
        adjustments = []
        
        # 体重变化评估
        weight_adjustment = self._should_adjust_by_weight(user, weight_history)
        if weight_adjustment.get('adjust', False):
            adjustments.append(weight_adjustment)
        
        # 体脂率评估
        if body_fat_history:
            bf_adjustment = self._should_adjust_by_body_fat(user, body_fat_history)
            if bf_adjustment.get('adjust', False):
                adjustments.append(bf_adjustment)
        
        # 执行情况评估
        compliance_adjustment = self._should_adjust_by_compliance(
            user, 
            daily_logs, 
            current_recommendation
        )
        if compliance_adjustment.get('adjust', False):
            adjustments.append(compliance_adjustment)
        
        # 训练表现评估
        performance_adjustment = self._should_adjust_by_performance(
            user,
            db
        )
        if performance_adjustment.get('adjust', False):
            adjustments.append(performance_adjustment)
        
        # 4. 综合决策
        if not adjustments:
            return current_recommendation  # 无需调整
        
        # 计算综合调整量（取平均值）
        total_adjustment = sum([adj.get('adjustment_kcal', 0) for adj in adjustments]) / len(adjustments)
        
        # 限制调整幅度
        total_adjustment = max(-self.max_adjustment_kcal, min(self.max_adjustment_kcal, total_adjustment))
        
        # 5. 应用调整
        new_kcal = current_recommendation.recommended_kcal + total_adjustment
        
        # 安全限制: 不低于BMR的1.1倍
        bmr = CalorieCalculatorService.get_user_bmr(user, prefer_katch_mcardle=True)
        min_kcal = bmr * self.min_kcal_multiplier
        new_kcal = max(new_kcal, min_kcal)
        
        # 6. 重新计算宏量营养素
        new_recommendation = self._recalculate_recommendation(user, new_kcal)
        
        # 7. 记录调整历史
        self._log_adjustment(
            db, 
            user.id, 
            current_recommendation, 
            new_recommendation, 
            adjustments
        )
        
        logging.info(
            f"Adjusted recommendation for user {user.id}: "
            f"{current_recommendation.recommended_kcal:.0f} -> {new_recommendation.recommended_kcal:.0f} kcal"
        )
        
        return new_recommendation
    
    def _can_adjust(self, db: Session, user_id: int) -> bool:
        """检查是否满足调整条件（时间间隔）"""
        latest_adjustment = recommendation_history.get_latest_adjustment(db, user_id=user_id)
        if not latest_adjustment:
            return True  # 从未调整过，可以调整
        
        days_since_last = (date.today() - latest_adjustment.adjustment_date).days
        return days_since_last >= self.min_adjustment_interval_days
    
    def _should_adjust_by_weight(
        self, 
        user: User, 
        weight_history: List[Tuple[date, float]]
    ) -> Dict:
        """
        基于体重变化判断是否需要调整
        返回: {'adjust': bool, 'adjustment_kcal': float, 'reason': str}
        """
        if len(weight_history) < 4:
            return {'adjust': False, 'reason': '体重数据不足（需要至少4周数据）'}
        
        # 计算最近4周的体重变化
        recent_weeks = weight_history[-4:]
        weight_change_per_week = (recent_weeks[-1][1] - recent_weeks[0][1]) / 4
        
        goal = user.goal
        
        if goal == 'lose_weight':
            # 减脂目标: 期望每周下降0.5-1kg
            if weight_change_per_week > -0.3:  # 下降太慢
                return {
                    'adjust': True,
                    'adjustment_kcal': -150,  # 减少150kcal
                    'reason': f'体重下降速度过慢({weight_change_per_week:.2f}kg/周，期望-0.5~-1kg/周)'
                }
            elif weight_change_per_week < -1.2:  # 下降太快
                return {
                    'adjust': True,
                    'adjustment_kcal': +150,  # 增加150kcal
                    'reason': f'体重下降速度过快，可能影响代谢({weight_change_per_week:.2f}kg/周)'
                }
        
        elif goal == 'gain_muscle':
            # 增肌目标: 期望每周增长0.1-0.3kg
            if weight_change_per_week < 0.05:  # 增长太慢
                return {
                    'adjust': True,
                    'adjustment_kcal': +150,
                    'reason': f'体重增长过慢({weight_change_per_week:.2f}kg/周，期望0.1~0.3kg/周)'
                }
            elif weight_change_per_week > 0.5:  # 增长太快（可能是脂肪）
                return {
                    'adjust': True,
                    'adjustment_kcal': -100,
                    'reason': f'体重增长过快，可能脂肪增长过多({weight_change_per_week:.2f}kg/周)'
                }
        
        return {'adjust': False, 'reason': '体重变化在合理范围内'}
    
    def _should_adjust_by_body_fat(
        self, 
        user: User, 
        body_fat_history: List[Tuple[date, float]]
    ) -> Dict:
        """
        增强的体脂率分析
        基于体脂率变化判断是否需要调整
        返回: {'adjust': bool, 'adjustment_kcal': float, 'reason': str}
        """
        if len(body_fat_history) < 2:
            return {'adjust': False, 'reason': '体脂率数据不足'}
        
        # 计算体脂率变化（最近2次测量）
        recent = body_fat_history[-2:]
        bf_change = recent[-1][1] - recent[0][1]
        days_between = (recent[-1][0] - recent[0][0]).days
        
        # 计算周变化率
        bf_change_per_week = (bf_change / days_between * 7) if days_between > 0 else 0
        
        goal = user.goal
        current_bf = recent[-1][1]
        
        if goal == 'lose_weight':
            # 减脂期: 如果体脂率上升，需要减少热量
            if bf_change > 0.5:
                return {
                    'adjust': True,
                    'adjustment_kcal': -100,
                    'reason': f'体脂率上升({bf_change:.1f}%，{bf_change_per_week:.2f}%/周)，需要减少热量'
                }
            # 如果体脂率下降但速度太慢，可能需要调整
            elif bf_change < -0.2 and bf_change_per_week > -0.3:
                return {
                    'adjust': True,
                    'adjustment_kcal': -50,
                    'reason': f'体脂率下降速度较慢({bf_change_per_week:.2f}%/周)，建议适当减少热量'
                }
            # 如果体脂率下降过快，可能流失肌肉
            elif bf_change < -1.5:
                return {
                    'adjust': True,
                    'adjustment_kcal': +50,
                    'reason': f'体脂率下降过快({bf_change:.1f}%)，可能流失肌肉，建议增加蛋白质'
                }
        
        elif goal == 'gain_muscle':
            # 增肌期: 如果体脂率上升过快，减少热量盈余
            if bf_change > 1.0:
                return {
                    'adjust': True,
                    'adjustment_kcal': -100,
                    'reason': f'体脂率上升过快({bf_change:.1f}%，{bf_change_per_week:.2f}%/周)，减少热量盈余'
                }
            # 如果体脂率上升但速度合理，保持
            elif bf_change > 0.3 and bf_change_per_week < 0.5:
                return {'adjust': False, 'reason': '体脂率上升速度合理'}
        
        elif goal == 'body_recomposition':
            # 体态重组: 需要特别精细的分析
            # 理想情况：体脂率下降，体重保持或略增
            if bf_change > 0.8:
                # 体脂率上升过多，减少热量
                return {
                    'adjust': True,
                    'adjustment_kcal': -75,
                    'reason': f'体态重组期体脂率上升({bf_change:.1f}%)，建议减少热量并增加蛋白质'
                }
            elif bf_change < -0.5 and current_bf < 15:
                # 体脂率下降且已较低，可能流失肌肉
                return {
                    'adjust': True,
                    'adjustment_kcal': +50,
                    'reason': f'体脂率已较低({current_bf:.1f}%)且继续下降，建议增加热量和蛋白质'
                }
        
        return {'adjust': False, 'reason': '体脂率变化正常'}
    
    def _should_adjust_by_compliance(
        self, 
        user: User,
        daily_logs: List[Dict],
        current_recommendation: CalorieRecommendation
    ) -> Dict:
        """
        基于用户实际执行情况调整
        返回: {'adjust': bool, 'adjustment_kcal': float, 'reason': str}
        """
        if len(daily_logs) < 7:
            return {'adjust': False, 'reason': '执行数据不足（需要至少7天数据）'}
        
        # 计算平均实际摄入
        avg_actual_kcal = sum([log.get('total_intake_kcal', 0) for log in daily_logs]) / len(daily_logs)
        recommended_kcal = current_recommendation.recommended_kcal
        
        if recommended_kcal == 0:
            return {'adjust': False, 'reason': '推荐热量为0，无法评估'}
        
        compliance_rate = avg_actual_kcal / recommended_kcal
        
        # 如果持续低于推荐值20%以上，适当降低推荐值
        if compliance_rate < 0.8:
            return {
                'adjust': True,
                'adjustment_kcal': -50,  # 减少50kcal
                'reason': f'实际摄入持续低于推荐({compliance_rate*100:.0f}%)，调整至更易执行的水平'
            }
        # 如果持续高于推荐值20%以上，适当提高推荐值
        elif compliance_rate > 1.2:
            return {
                'adjust': True,
                'adjustment_kcal': +50,  # 增加50kcal
                'reason': f'实际摄入持续高于推荐({compliance_rate*100:.0f}%)，调整至更符合实际需求'
            }
        
        return {'adjust': False, 'reason': '执行情况正常'}
    
    def _should_adjust_by_performance(
        self,
        user: User,
        db: Session
    ) -> Dict:
        """
        基于训练表现判断是否需要调整
        返回: {'adjust': bool, 'adjustment_kcal': float, 'reason': str}
        """
        try:
            performance_data = performance_analysis_service.analyze_training_performance(
                user=user,
                db=db,
                weeks=4
            )
            
            if not performance_data.get('has_data', False):
                return {'adjust': False, 'reason': '训练数据不足'}
            
            goal = user.goal
            overall_trend = performance_data.get('overall_trend', {})
            strength_trend = performance_data.get('strength_trend', {})
            
            # 增肌目标：如果力量训练表现下降，可能是热量不足
            if goal == 'gain_muscle':
                if strength_trend.get('trend') == 'declining':
                    return {
                        'adjust': True,
                        'adjustment_kcal': +100,
                        'reason': '力量训练表现下降，可能热量不足，建议增加热量'
                    }
                elif overall_trend.get('trend') == 'declining':
                    return {
                        'adjust': True,
                        'adjustment_kcal': +50,
                        'reason': '总体训练量下降，建议适当增加热量'
                    }
            
            # 减脂目标：如果训练量下降，可能需要调整
            elif goal == 'lose_weight':
                if overall_trend.get('trend') == 'declining':
                    # 训练量下降，可能需要减少热量推荐（因为消耗减少）
                    return {
                        'adjust': True,
                        'adjustment_kcal': -50,
                        'reason': '训练量下降，相应减少热量推荐'
                    }
            
            # 体态重组：需要特别关注训练表现
            elif goal == 'body_recomposition':
                if strength_trend.get('trend') == 'declining':
                    return {
                        'adjust': True,
                        'adjustment_kcal': +75,
                        'reason': '体态重组期力量训练下降，建议增加热量和蛋白质'
                    }
            
        except Exception as e:
            logging.warning(f"Performance analysis failed for user {user.id}: {e}")
            return {'adjust': False, 'reason': '训练表现分析失败'}
        
        return {'adjust': False, 'reason': '训练表现正常'}
    
    def _get_daily_logs(self, db: Session, user_id: int, days: int) -> List[Dict]:
        """获取最近N天的饮食日志汇总"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        food_logs = log.get_food_logs_by_user_and_date_range(
            db, 
            user_id=user_id, 
            start_date=start_date, 
            end_date=end_date
        )
        
        # 按日期汇总
        daily_summary = {}
        for food_log in food_logs:
            log_date = food_log.log_date
            if log_date not in daily_summary:
                daily_summary[log_date] = {'total_intake_kcal': 0}
            
            if food_log.total_calories:
                daily_summary[log_date]['total_intake_kcal'] += float(food_log.total_calories)
        
        return list(daily_summary.values())
    
    def _recalculate_recommendation(
        self, 
        user: User, 
        new_kcal: float
    ) -> CalorieRecommendation:
        """重新计算推荐（基于新的热量值）"""
        # 计算热量区间
        tdee = CalorieCalculatorService.get_user_tdee(user, prefer_katch_mcardle=True)
        calorie_range = calculate_calorie_range(user, tdee)
        
        # 计算宏量营养素
        macros = calculate_all_macros(user, new_kcal)
        
        protein = macros['protein']
        fat = macros['fat']
        carbs = macros['carbs']
        
        return CalorieRecommendation(
            goal=user.goal.replace('_', ' ').title(),
            recommended_kcal=round(new_kcal, 2),
            min_kcal=round(calorie_range['min_kcal'], 2),
            max_kcal=round(calorie_range['max_kcal'], 2),
            protein_g=round(protein['recommended_g'], 2),
            protein_min_g=round(protein['min_g'], 2),
            protein_max_g=round(protein['max_g'], 2),
            fat_g=round(fat['recommended_g'], 2),
            fat_min_g=round(fat['min_g'], 2),
            fat_max_g=round(fat['max_g'], 2),
            carbs_g=round(carbs['recommended_g'], 2),
            range_description=calorie_range['range_description']
        )
    
    def _log_adjustment(
        self,
        db: Session,
        user_id: int,
        previous_recommendation: CalorieRecommendation,
        new_recommendation: CalorieRecommendation,
        adjustments: List[Dict]
    ):
        """记录调整历史"""
        from app.schemas.recommendation_history import RecommendationHistoryCreate
        
        # 提取触发因素
        trigger_factors = {
            'reasons': [adj.get('reason', '') for adj in adjustments],
            'adjustment_count': len(adjustments)
        }
        
        history_in = RecommendationHistoryCreate(
            adjustment_date=date.today(),
            previous_kcal=previous_recommendation.recommended_kcal,
            previous_protein_g=previous_recommendation.protein_g,
            previous_fat_g=previous_recommendation.fat_g,
            previous_carbs_g=previous_recommendation.carbs_g,
            new_kcal=new_recommendation.recommended_kcal,
            new_protein_g=new_recommendation.protein_g,
            new_fat_g=new_recommendation.fat_g,
            new_carbs_g=new_recommendation.carbs_g,
            adjustment_reason='; '.join([adj.get('reason', '') for adj in adjustments]),
            trigger_factors=trigger_factors
        )
        
        recommendation_history.create_recommendation_history(
            db, 
            user_id=user_id, 
            history_in=history_in
        )


# 创建全局实例
dynamic_adjustment_service = DynamicAdjustmentService()
