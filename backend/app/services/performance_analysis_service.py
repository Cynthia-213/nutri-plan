"""
训练表现分析服务
分析用户的运动日志，评估训练表现趋势
"""
import logging
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from collections import defaultdict

from app.models.user import User
from app.crud.crud_log import log


class PerformanceAnalysisService:
    """
    训练表现分析服务
    分析运动日志，识别训练表现趋势
    """
    
    # 力量训练关键词（用于识别力量训练）
    STRENGTH_KEYWORDS = [
        '力量', '举重', '深蹲', '硬拉', '卧推', '推举', '划船',
        'strength', 'weight', 'squat', 'deadlift', 'bench', 'press', 'row'
    ]
    
    # 有氧训练关键词（用于识别有氧训练）
    CARDIO_KEYWORDS = [
        '跑步', '慢跑', '快走', '游泳', '骑行', '跳绳', '有氧',
        'run', 'jog', 'walk', 'swim', 'bike', 'cycle', 'cardio', 'hiit'
    ]
    
    def analyze_training_performance(
        self,
        user: User,
        db: Session,
        weeks: int = 4
    ) -> Dict:
        """
        分析用户的训练表现
        
        :param user: 用户对象
        :param db: 数据库会话
        :param weeks: 分析的时间范围（周）
        :return: 包含分析结果的字典
        """
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks)
        
        # 获取运动日志
        exercise_logs = log.get_exercise_logs_by_user_and_date_range(
            db,
            user_id=user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not exercise_logs:
            return {
                'has_data': False,
                'message': '没有足够的运动数据进行分析'
            }
        
        # 分析总体趋势
        overall_trend = self._analyze_overall_trend(exercise_logs)
        
        # 分析力量训练趋势
        strength_trend = self._analyze_strength_trend(exercise_logs)
        
        # 分析有氧训练趋势
        cardio_trend = self._analyze_cardio_trend(exercise_logs)
        
        # 分析训练频率
        frequency_analysis = self._analyze_training_frequency(exercise_logs, start_date, end_date)
        
        # 分析训练强度
        intensity_analysis = self._analyze_training_intensity(exercise_logs)
        
        return {
            'has_data': True,
            'overall_trend': overall_trend,
            'strength_trend': strength_trend,
            'cardio_trend': cardio_trend,
            'frequency': frequency_analysis,
            'intensity': intensity_analysis,
            'summary': self._generate_summary(
                overall_trend, 
                strength_trend, 
                cardio_trend,
                user.goal
            )
        }
    
    def _analyze_overall_trend(
        self,
        exercise_logs: List
    ) -> Dict:
        """
        分析总体训练趋势
        基于总训练时长和总消耗热量
        """
        # 按周分组
        weekly_data = defaultdict(lambda: {'duration': 0, 'calories': 0})
        
        for log_entry in exercise_logs:
            week_key = log_entry.log_date.isocalendar()[1]  # 周数
            weekly_data[week_key]['duration'] += log_entry.duration_minutes
            weekly_data[week_key]['calories'] += float(log_entry.calories_burned or 0)
        
        if len(weekly_data) < 2:
            return {
                'trend': 'insufficient_data',
                'message': '数据不足，无法分析趋势'
            }
        
        # 计算趋势
        weeks = sorted(weekly_data.keys())
        recent_weeks = weeks[-2:]  # 最近2周
        
        recent_avg_duration = sum([weekly_data[w]['duration'] for w in recent_weeks]) / len(recent_weeks)
        earlier_avg_duration = sum([weekly_data[w]['duration'] for w in weeks[:-2]]) / max(1, len(weeks) - 2)
        
        duration_change_pct = ((recent_avg_duration - earlier_avg_duration) / max(earlier_avg_duration, 1)) * 100
        
        if duration_change_pct > 10:
            trend = 'improving'
            message = f'训练量增加{duration_change_pct:.1f}%'
        elif duration_change_pct < -10:
            trend = 'declining'
            message = f'训练量减少{abs(duration_change_pct):.1f}%'
        else:
            trend = 'stable'
            message = '训练量保持稳定'
        
        return {
            'trend': trend,
            'message': message,
            'duration_change_pct': round(duration_change_pct, 1),
            'recent_avg_duration': round(recent_avg_duration, 0),
            'earlier_avg_duration': round(earlier_avg_duration, 0)
        }
    
    def _analyze_strength_trend(
        self,
        exercise_logs: List
    ) -> Dict:
        """
        分析力量训练趋势
        基于力量训练的运动时长和频率
        """
        strength_logs = [
            log_entry for log_entry in exercise_logs
            if self._is_strength_training(log_entry)
        ]
        
        if len(strength_logs) < 4:
            return {
                'trend': 'insufficient_data',
                'message': '力量训练数据不足'
            }
        
        # 按周分组
        weekly_data = defaultdict(lambda: {'duration': 0, 'count': 0})
        
        for log_entry in strength_logs:
            week_key = log_entry.log_date.isocalendar()[1]
            weekly_data[week_key]['duration'] += log_entry.duration_minutes
            weekly_data[week_key]['count'] += 1
        
        weeks = sorted(weekly_data.keys())
        if len(weeks) < 2:
            return {
                'trend': 'insufficient_data',
                'message': '力量训练数据不足'
            }
        
        recent_weeks = weeks[-2:]
        earlier_weeks = weeks[:-2] if len(weeks) > 2 else [weeks[0]]
        
        recent_avg_duration = sum([weekly_data[w]['duration'] for w in recent_weeks]) / len(recent_weeks)
        earlier_avg_duration = sum([weekly_data[w]['duration'] for w in earlier_weeks]) / len(earlier_weeks)
        
        duration_change_pct = ((recent_avg_duration - earlier_avg_duration) / max(earlier_avg_duration, 1)) * 100
        
        if duration_change_pct > 15:
            trend = 'improving'
            message = f'力量训练量增加{duration_change_pct:.1f}%'
        elif duration_change_pct < -15:
            trend = 'declining'
            message = f'力量训练量减少{abs(duration_change_pct):.1f}%'
        else:
            trend = 'stable'
            message = '力量训练量保持稳定'
        
        return {
            'trend': trend,
            'message': message,
            'duration_change_pct': round(duration_change_pct, 1),
            'recent_avg_duration': round(recent_avg_duration, 0),
            'frequency': sum([weekly_data[w]['count'] for w in recent_weeks]) / len(recent_weeks)
        }
    
    def _analyze_cardio_trend(
        self,
        exercise_logs: List
    ) -> Dict:
        """
        分析有氧训练趋势
        基于有氧训练的运动时长和频率
        """
        cardio_logs = [
            log_entry for log_entry in exercise_logs
            if self._is_cardio_training(log_entry)
        ]
        
        if len(cardio_logs) < 4:
            return {
                'trend': 'insufficient_data',
                'message': '有氧训练数据不足'
            }
        
        # 按周分组
        weekly_data = defaultdict(lambda: {'duration': 0, 'calories': 0})
        
        for log_entry in cardio_logs:
            week_key = log_entry.log_date.isocalendar()[1]
            weekly_data[week_key]['duration'] += log_entry.duration_minutes
            weekly_data[week_key]['calories'] += float(log_entry.calories_burned or 0)
        
        weeks = sorted(weekly_data.keys())
        if len(weeks) < 2:
            return {
                'trend': 'insufficient_data',
                'message': '有氧训练数据不足'
            }
        
        recent_weeks = weeks[-2:]
        earlier_weeks = weeks[:-2] if len(weeks) > 2 else [weeks[0]]
        
        recent_avg_duration = sum([weekly_data[w]['duration'] for w in recent_weeks]) / len(recent_weeks)
        earlier_avg_duration = sum([weekly_data[w]['duration'] for w in earlier_weeks]) / len(earlier_weeks)
        
        duration_change_pct = ((recent_avg_duration - earlier_avg_duration) / max(earlier_avg_duration, 1)) * 100
        
        if duration_change_pct > 10:
            trend = 'improving'
            message = f'有氧训练量增加{duration_change_pct:.1f}%'
        elif duration_change_pct < -10:
            trend = 'declining'
            message = f'有氧训练量减少{abs(duration_change_pct):.1f}%'
        else:
            trend = 'stable'
            message = '有氧训练量保持稳定'
        
        return {
            'trend': trend,
            'message': message,
            'duration_change_pct': round(duration_change_pct, 1),
            'recent_avg_duration': round(recent_avg_duration, 0)
        }
    
    def _analyze_training_frequency(
        self,
        exercise_logs: List,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        分析训练频率
        """
        training_days = set([log_entry.log_date for log_entry in exercise_logs])
        total_days = (end_date - start_date).days + 1
        training_days_count = len(training_days)
        
        frequency = (training_days_count / total_days) * 100 if total_days > 0 else 0
        
        return {
            'training_days': training_days_count,
            'total_days': total_days,
            'frequency_pct': round(frequency, 1),
            'avg_days_per_week': round((training_days_count / max(1, total_days / 7)), 1)
        }
    
    def _analyze_training_intensity(
        self,
        exercise_logs: List
    ) -> Dict:
        """
        分析训练强度
        基于平均MET值和总消耗
        """
        if not exercise_logs:
            return {
                'avg_met': 0,
                'total_calories': 0,
                'intensity_level': 'low'
            }
        
        total_calories = sum([float(log_entry.calories_burned or 0) for log_entry in exercise_logs])
        total_duration = sum([log_entry.duration_minutes for log_entry in exercise_logs])
        
        # 计算平均MET（简化计算）
        met_values = []
        for log_entry in exercise_logs:
            if log_entry.exercise and log_entry.exercise.met_value:
                met_values.append(float(log_entry.exercise.met_value))
        
        avg_met = sum(met_values) / len(met_values) if met_values else 0
        
        # 判断强度水平
        if avg_met >= 6.0:
            intensity_level = 'high'
        elif avg_met >= 3.0:
            intensity_level = 'moderate'
        else:
            intensity_level = 'low'
        
        return {
            'avg_met': round(avg_met, 2),
            'total_calories': round(total_calories, 0),
            'total_duration_minutes': total_duration,
            'intensity_level': intensity_level
        }
    
    def _is_strength_training(self, log_entry) -> bool:
        """判断是否为力量训练"""
        if not log_entry.exercise:
            return False
        
        exercise_name = log_entry.exercise.name.lower()
        return any(keyword in exercise_name for keyword in self.STRENGTH_KEYWORDS)
    
    def _is_cardio_training(self, log_entry) -> bool:
        """判断是否为有氧训练"""
        if not log_entry.exercise:
            return False
        
        exercise_name = log_entry.exercise.name.lower()
        return any(keyword in exercise_name for keyword in self.CARDIO_KEYWORDS)
    
    def _generate_summary(
        self,
        overall_trend: Dict,
        strength_trend: Dict,
        cardio_trend: Dict,
        goal: str
    ) -> str:
        """生成分析摘要"""
        summary_parts = []
        
        if overall_trend.get('trend') == 'declining':
            summary_parts.append('总体训练量下降')
        elif overall_trend.get('trend') == 'improving':
            summary_parts.append('总体训练量提升')
        
        if goal == 'gain_muscle':
            if strength_trend.get('trend') == 'declining':
                summary_parts.append('力量训练量下降，可能影响增肌效果')
            elif strength_trend.get('trend') == 'improving':
                summary_parts.append('力量训练量提升，增肌效果良好')
        
        if goal == 'lose_weight':
            if cardio_trend.get('trend') == 'declining':
                summary_parts.append('有氧训练量下降，可能影响减脂效果')
            elif cardio_trend.get('trend') == 'improving':
                summary_parts.append('有氧训练量提升，减脂效果良好')
        
        return '；'.join(summary_parts) if summary_parts else '训练表现正常'


# 创建全局实例
performance_analysis_service = PerformanceAnalysisService()
