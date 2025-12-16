from datetime import date
from app.models.user import User


# 基于活动水平的TDEE乘数
ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,        # 久坐（很少或没有运动）
    'lightly_active': 1.375, # 轻度活跃（每周1-3天轻度运动）
    'moderately_active': 1.55, # 中度活跃（每周3-5天中度运动）
    'very_active': 1.725,    # 非常活跃（每周6-7天高强度运动）
    'extra_active': 1.9,     # 极度活跃（体力劳动者或专业运动员）
}

def calculate_age(birthdate: date) -> int:
    """根据出生日期计算当前年龄"""
    if not birthdate:
        return 0
    today = date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def calculate_bmr(user: User) -> float:
    """
    使用 Mifflin-St Jeor 公式计算基础代谢率 (BMR)，这是维持生命所需的最基本能量
    :param user: 包含性别、体重、身高和出生日期的用户对象
    :return: BMR值（千卡/天）
    """
    if not all([user.weight_kg, user.height_cm, user.birthdate, user.gender]):
        # 如果缺少必要信息，无法计算，返回0或默认值
        
        return 0.0

    age = calculate_age(user.birthdate)
    
    # Mifflin-St Jeor 公式
    # BMR (kcal/day) = 10 * weight (kg) + 6.25 * height (cm) - 5 * age (y) + s
    # s 是一个性别常数: 男性为 +5, 女性为 -161
    if user.gender == 'male':
        s = 5
    elif user.gender == 'female':
        s = -161

    bmr = (10 * float(user.weight_kg)) + (6.25 * float(user.height_cm)) - (5 * age) + s
    
    return max(0, bmr) # 确保BMR不为负

def calculate_tdee(user: User, bmr: float = None) -> float:
    """
    计算总日能量消耗 (Total Daily Energy Expenditure, TDEE)
    这是BMR乘以活动水平系数得出的每日总热量消耗
    :param user: 包含活动水平的用户对象
    :param bmr: 基础代谢率，如果未提供，将重新计算
    :return: TDEE值（千卡/天）
    """
    if bmr is None:
        bmr = calculate_bmr(user)
    
    multiplier = ACTIVITY_MULTIPLIERS.get(user.activity_level, 1.2)
    
    return bmr * multiplier

def calculate_exercise_calories_burned(
    met_value: float, weight_kg: float, duration_minutes: int
) -> float:
    """
    计算特定运动消耗的热量
    公式: 热量 (kcal) = MET * 体重 (kg) * 运动时长 (小时)
    :param met_value: 运动的代谢当量 (MET)
    :param weight_kg: 用户的体重（公斤）
    :param duration_minutes: 运动时长（分钟）
    :return: 消耗的热量（千卡）
    """
    if not all([met_value, weight_kg, duration_minutes]):
        return 0.0
        
    duration_hours = duration_minutes / 60.0
    calories_burned = met_value * weight_kg * duration_hours
    
    return calories_burned

class CalorieCalculatorService:
    """
    一个封装了所有热量计算逻辑的服务类
    """
    @staticmethod
    def get_user_bmr(user: User) -> float:
        return calculate_bmr(user)

    @staticmethod
    def get_user_tdee(user: User) -> float:
        bmr = calculate_bmr(user)
        return calculate_tdee(user, bmr)

    @staticmethod
    def get_exercise_calories(met_value: float, weight_kg: float, duration_minutes: int) -> float:
        return calculate_exercise_calories_burned(met_value, weight_kg, duration_minutes)

