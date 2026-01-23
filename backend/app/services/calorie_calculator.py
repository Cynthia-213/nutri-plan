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

def calculate_bmr_mifflin_st_jeor(user: User) -> float:
    """
    使用 Mifflin-St Jeor 公式计算基础代谢率 (BMR)
    这是维持生命所需的最基本能量
    :param user: 包含性别、体重、身高和出生日期的用户对象
    :return: BMR值（千卡/天）
    """
    if not all([user.weight_kg, user.height_cm, user.birthdate, user.gender]):
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

    return max(0, bmr)

def calculate_bmr_katch_mcardle(user: User) -> float:
    """
    使用 Katch-McArdle 公式计算基础代谢率 (BMR)
    需要体脂率数据，对于高体脂人群更准确
    公式: BMR = 370 + (21.6 × 去脂体重(kg))
    去脂体重(FFM) = 体重(kg) × (1 - 体脂率/100)
    :param user: 包含体重和体脂率的用户对象
    :return: BMR值（千卡/天），如果缺少体脂率则返回0
    """
    if not user.weight_kg or not user.body_fat_pct:
        return 0.0

    weight_kg = float(user.weight_kg)
    body_fat_pct = float(user.body_fat_pct)

    # 计算去脂体重 (Fat-Free Mass, FFM)
    fat_free_mass = weight_kg * (1 - body_fat_pct / 100)
    # Katch-McArdle 公式
    bmr = 370 + (21.6 * fat_free_mass)

    return max(0, bmr)

def calculate_bmr(user: User, prefer_katch_mcardle: bool = False) -> float:
    """
    计算基础代谢率 (BMR)
    优先使用Katch-McArdle公式（如果有体脂率数据），否则使用Mifflin-St Jeor公式
    :param user: 用户对象
    :param prefer_katch_mcardle: 如果为True且用户有体脂率数据，优先使用Katch-McArdle公式
    :return: BMR值（千卡/天）
    """
    # 如果用户有体脂率数据且prefer_katch_mcardle为True，使用Katch-McArdle公式
    if prefer_katch_mcardle and user.body_fat_pct:
        bmr = calculate_bmr_katch_mcardle(user)
        if bmr > 0:
            return bmr
    
    # 否则使用Mifflin-St Jeor公式
    return calculate_bmr_mifflin_st_jeor(user)

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

def calculate_exercise_calories_burned(met_value: float, weight_kg: float, duration_minutes: int) -> float:
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
    def get_user_bmr(user: User, prefer_katch_mcardle: bool = True) -> float:
        """
        获取用户BMR
        :param user: 用户对象
        :param prefer_katch_mcardle: 如果有体脂率数据，是否优先使用Katch-McArdle公式
        :return: BMR值
        """
        return calculate_bmr(user, prefer_katch_mcardle=prefer_katch_mcardle)

    @staticmethod
    def get_user_tdee(user: User, prefer_katch_mcardle: bool = True) -> float:
        """
        获取用户TDEE
        :param user: 用户对象
        :param prefer_katch_mcardle: 如果有体脂率数据，是否优先使用Katch-McArdle公式计算BMR
        :return: TDEE值
        """
        bmr = calculate_bmr(user, prefer_katch_mcardle=prefer_katch_mcardle)
        return calculate_tdee(user, bmr)

    @staticmethod
    def get_exercise_calories(met_value: float, weight_kg: float, duration_minutes: int) -> float:
        return calculate_exercise_calories_burned(met_value, weight_kg, duration_minutes)

