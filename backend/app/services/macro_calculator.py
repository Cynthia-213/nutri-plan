from typing import Dict, Optional
from app.models.user import User


# 每克营养素的热量 (千卡)
CALORIES_PER_GRAM = {
    'protein': 4,
    'fat': 9,
    'carbs': 4
}

def calculate_protein_requirement(user: User, goal: str) -> Dict[str, float]:
    """
    计算蛋白质需求（基于体重）
    科学依据:
    - 维持: 0.8-1.0 g/kg
    - 增肌: 1.6-2.2 g/kg (推荐1.8-2.0 g/kg)
    - 减脂: 1.6-2.2 g/kg (高蛋白有助于保持肌肉)
    - 体态重组: 2.0-2.4 g/kg (最高需求)
    
    :param user: 用户对象
    :param goal: 用户目标
    :return: {
        'min_g': 最低克数,
        'recommended_g': 推荐克数,
        'max_g': 最高克数,
        'g_per_kg': 每公斤体重克数
    }
    """
    weight_kg = float(user.weight_kg)
    
    # 根据目标和性别确定蛋白质需求
    if goal == 'maintain':
        g_per_kg = {'min': 0.8, 'recommended': 0.9, 'max': 1.0}
    elif goal == 'lose_weight':
        # 减脂期需要高蛋白，女性可能需要更高
        if user.gender == 'female':
            g_per_kg = {'min': 1.8, 'recommended': 2.0, 'max': 2.2}
        else:
            g_per_kg = {'min': 1.6, 'recommended': 1.8, 'max': 2.2}
    elif goal == 'gain_muscle':
        if user.training_experience == 'beginner':
            g_per_kg = {'min': 1.6, 'recommended': 1.8, 'max': 2.0}
        else:
            g_per_kg = {'min': 1.8, 'recommended': 2.0, 'max': 2.2}
    elif goal == 'body_recomposition':
        g_per_kg = {'min': 2.0, 'recommended': 2.2, 'max': 2.4}
    else:  # gain_weight
        g_per_kg = {'min': 1.2, 'recommended': 1.4, 'max': 1.6}
    
    return {
        'min_g': round(weight_kg * g_per_kg['min'], 1),
        'recommended_g': round(weight_kg * g_per_kg['recommended'], 1),
        'max_g': round(weight_kg * g_per_kg['max'], 1),
        'g_per_kg': g_per_kg['recommended']
    }


def calculate_fat_requirement(total_kcal: float, goal: str, gender: str) -> Dict[str, float]:
    """
    计算脂肪需求（基于总热量百分比）
    科学依据:
    - 最低需求: 15-20%总热量 (保证必需脂肪酸)
    - 推荐范围: 20-35%总热量
    - 减脂期: 25-30% (增加饱腹感)
    - 增肌期: 20-25% (为碳水留出空间)
    - 女性: 不低于25% (对激素平衡重要)
    
    :param total_kcal: 总热量（使用推荐热量）
    :param goal: 用户目标
    :param gender: 用户性别
    :return: {
        'min_g': 最低克数,
        'recommended_g': 推荐克数,
        'max_g': 最高克数,
        'percentage': 占总热量百分比
    }
    """
    if goal == 'lose_weight':
        fat_pct = {'min': 0.25, 'recommended': 0.28, 'max': 0.30}
    elif goal == 'gain_muscle':
        fat_pct = {'min': 0.20, 'recommended': 0.23, 'max': 0.25}
    elif goal == 'body_recomposition':
        fat_pct = {'min': 0.22, 'recommended': 0.25, 'max': 0.28}
    else:  # maintain, gain_weight
        fat_pct = {'min': 0.25, 'recommended': 0.30, 'max': 0.35}
    
    # 女性最低脂肪需求不低于25%
    if gender == 'female':
        fat_pct['min'] = max(fat_pct['min'], 0.25)
        if fat_pct['recommended'] < 0.25:
            fat_pct['recommended'] = 0.25
    
    recommended_kcal = total_kcal * fat_pct['recommended']
    recommended_g = recommended_kcal / CALORIES_PER_GRAM['fat']
    
    return {
        'min_g': round(total_kcal * fat_pct['min'] / CALORIES_PER_GRAM['fat'], 1),
        'recommended_g': round(recommended_g, 1),
        'max_g': round(total_kcal * fat_pct['max'] / CALORIES_PER_GRAM['fat'], 1),
        'percentage': round(fat_pct['recommended'] * 100, 1)
    }


def calculate_carb_requirement(
    total_kcal: float,
    protein_g: float,
    fat_g: float,
    activity_level: str
) -> Dict[str, float]:
    """
    计算碳水化合物需求（剩余热量原则）
    总热量 - 蛋白质热量 - 脂肪热量 = 碳水热量
    
    :param total_kcal: 总热量
    :param protein_g: 蛋白质克数（使用推荐值）
    :param fat_g: 脂肪克数（使用推荐值）
    :param activity_level: 活动水平
    :return: {
        'recommended_g': 推荐克数,
        'percentage': 占总热量百分比
    }
    """
    protein_kcal = protein_g * CALORIES_PER_GRAM['protein']
    fat_kcal = fat_g * CALORIES_PER_GRAM['fat']
    carb_kcal = total_kcal - protein_kcal - fat_kcal
    carb_g = carb_kcal / CALORIES_PER_GRAM['carbs']
    
    # 高活动人群可适当提高碳水
    if activity_level in ['very_active', 'extra_active']:
        # 如果碳水比例低于40%，可以适当调整
        carb_percentage = (carb_kcal / total_kcal) * 100
        if carb_percentage < 40:
            # 从脂肪中调整一些热量给碳水
            adjustment_kcal = total_kcal * 0.05  # 调整5%
            carb_kcal = carb_kcal + adjustment_kcal
            carb_g = carb_kcal / CALORIES_PER_GRAM['carbs']
    
    return {
        'recommended_g': round(carb_g, 1),
        'percentage': round((carb_kcal / total_kcal) * 100, 1)
    }


def calculate_all_macros(user: User, recommended_kcal: float) -> Dict:
    """
    计算所有宏量营养素需求
    
    :param user: 用户对象
    :param recommended_kcal: 推荐热量
    :return: 包含所有宏量营养素信息的字典
    """
    goal = user.goal
    
    # 1. 计算蛋白质
    protein = calculate_protein_requirement(user, goal)
    
    # 2. 计算脂肪
    fat = calculate_fat_requirement(recommended_kcal, goal, user.gender)
    
    # 3. 计算碳水（剩余热量原则）
    carbs = calculate_carb_requirement(
        recommended_kcal,
        protein['recommended_g'],
        fat['recommended_g'],
        user.activity_level
    )
    
    return {
        'protein': protein,
        'fat': fat,
        'carbs': carbs
    }
