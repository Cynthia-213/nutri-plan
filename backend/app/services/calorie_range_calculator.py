from typing import Dict, Optional
from app.models.user import User


def calculate_calorie_range(user: User, tdee: float) -> Dict[str, float]:
    """
    计算热量区间
    根据用户目标和体脂率，返回最低、推荐、最高热量值
    
    :param user: 用户对象
    :param tdee: 用户的总日能量消耗
    :return: {
        'min_kcal': 最低热量,
        'recommended_kcal': 推荐热量,
        'max_kcal': 最高热量,
        'range_description': '区间说明'
    }
    """
    goal = user.goal
    body_fat_pct = float(user.body_fat_pct) if user.body_fat_pct else None
    
    if goal == 'lose_weight':
        return _calculate_lose_weight_range(tdee, body_fat_pct)
    elif goal == 'gain_muscle':
        return _calculate_gain_muscle_range(tdee, user.training_experience)
    elif goal == 'gain_weight':
        return _calculate_gain_weight_range(tdee)
    elif goal == 'body_recomposition':
        return _calculate_body_recomposition_range(tdee)
    else:
        return _calculate_maintain_range(tdee)


def _calculate_lose_weight_range(tdee: float, body_fat_pct: Optional[float]) -> Dict[str, float]:
    """
    计算减脂热量区间
    科学依据: 安全减脂速度每周0.5-1kg，热量赤字10-25% TDEE
    """
    # 根据体脂率调整赤字幅度
    if body_fat_pct and body_fat_pct > 30:
        # 高体脂人群可接受更大赤字
        deficit_pct = 0.25
        min_deficit_pct = 0.20
        max_deficit_pct = 0.30
    elif body_fat_pct and body_fat_pct < 15:
        # 低体脂人群保守减脂
        deficit_pct = 0.15
        min_deficit_pct = 0.10
        max_deficit_pct = 0.20
    else:
        # 标准赤字
        deficit_pct = 0.20
        min_deficit_pct = 0.15
        max_deficit_pct = 0.25
    
    return {
        'min_kcal': round(tdee * (1 - max_deficit_pct), 0),
        'recommended_kcal': round(tdee * (1 - deficit_pct), 0),
        'max_kcal': round(tdee * (1 - min_deficit_pct), 0),
        'range_description': f'减脂区间: {deficit_pct*100:.0f}%热量赤字（建议每周体重下降0.5-1kg）'
    }

def _calculate_gain_muscle_range(tdee: float, training_experience: str) -> Dict[str, float]:
    """
    计算增肌热量区间
    科学依据: 自然增肌需要5-15%热量盈余，新手可接受更高盈余
    """
    if training_experience == 'beginner':
        # 初学者可接受更高盈余
        surplus_pct = 0.15
        min_surplus_pct = 0.10
        max_surplus_pct = 0.20
    elif training_experience == 'advanced':
        # 有经验训练者建议保守盈余
        surplus_pct = 0.08
        min_surplus_pct = 0.05
        max_surplus_pct = 0.12
    else:
        # 中等经验标准盈余
        surplus_pct = 0.10
        min_surplus_pct = 0.05
        max_surplus_pct = 0.15
    
    return {
        'min_kcal': round(tdee * (1 + min_surplus_pct), 0),
        'recommended_kcal': round(tdee * (1 + surplus_pct), 0),
        'max_kcal': round(tdee * (1 + max_surplus_pct), 0),
        'range_description': f'增肌区间: {surplus_pct*100:.0f}%热量盈余（{training_experience}训练者）'
    }

def _calculate_gain_weight_range(tdee: float) -> Dict[str, float]:
    """
    计算增重热量区间
    适用于低体重人群(BMI<18.5)
    """
    surplus_pct = 0.15
    min_surplus_pct = 0.10
    max_surplus_pct = 0.20
    
    return {
        'min_kcal': round(tdee * (1 + min_surplus_pct), 0),
        'recommended_kcal': round(tdee * (1 + surplus_pct), 0),
        'max_kcal': round(tdee * (1 + max_surplus_pct), 0),
        'range_description': '增重区间: 15%热量盈余（适用于低体重人群）'
    }

def _calculate_body_recomposition_range(tdee: float) -> Dict[str, float]:
    """
    增强的体态重组热量区间计算
    同时减脂增肌，需要接近维持热量或轻微赤字
    根据体脂率和训练经验微调
    """
    # 基础区间：接近维持热量
    base_min = tdee * 0.95 # 5%赤字
    base_recommended = tdee * 1.00 # 维持热量
    base_max = tdee * 1.05 # 5%盈余
    
    return {
        'min_kcal': round(base_min, 0),
        'recommended_kcal': round(base_recommended, 0),
        'max_kcal': round(base_max, 0),
        'range_description': '体态重组区间: 接近维持热量（需配合高蛋白2.0-2.4g/kg和规律力量训练，建议每周3-4次）'
    }

def _calculate_maintain_range(tdee: float) -> Dict[str, float]:
    """
    计算维持热量区间
    允许5%波动
    """
    return {
        'min_kcal': round(tdee * 0.95, 0),
        'recommended_kcal': round(tdee * 1.00, 0),
        'max_kcal': round(tdee * 1.05, 0),
        'range_description': '维持区间: 允许5%热量波动'
    }