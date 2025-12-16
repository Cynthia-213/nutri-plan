import logging
from app.models.user import User
from app.services.calorie_calculator import CalorieCalculatorService
from app.schemas.log import CalorieRecommendation


# 目标热量调整 (千卡/天)
GOAL_ADJUSTMENT = {
    'lose_weight': -500,  # 减脂：建议每天减少500千卡热量摄入
    'gain_muscle': 300,   # 增肌：建议每天增加300千卡热量摄入
    'maintain': 0         # 维持：保持热量平衡
}

# 三大营养素供能比例 (%)
MACRO_RATIOS = {
    'standard': {'protein': 0.20, 'fat': 0.30, 'carbs': 0.50},       # 标准均衡
    'lose_weight': {'protein': 0.30, 'fat': 0.30, 'carbs': 0.40},   # 减脂 (略高蛋白)
    'gain_muscle': {'protein': 0.35, 'fat': 0.25, 'carbs': 0.40}    # 增肌 (高蛋白)
}

# 每克营养素的热量 (千卡)
CALORIES_PER_GRAM = {
    'protein': 4,
    'fat': 9,
    'carbs': 4
}


class RecommendationService:
    """
    提供饮食和营养建议的服务
    """
    @staticmethod
    def get_calorie_recommendation(user: User) -> CalorieRecommendation:
        """
        根据用户的目标，计算推荐的每日热量和三大营养素摄入量。
        
        :param user: 用户对象
        :return: 一个包含推荐值的 Pydantic 模型
        """
        # 1. 计算用户的TDEE (总日能量消耗)
        tdee = CalorieCalculatorService.get_user_tdee(user)
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

        # 根据用户目标调整每日推荐热量
        adjustment = GOAL_ADJUSTMENT.get(user.goal, 0)
        recommended_kcal = tdee + adjustment

        # 根据目标选择合适的宏量营养素比例
        ratios = MACRO_RATIOS.get(user.goal, MACRO_RATIOS['standard'])

        # 计算各种宏量营养素的推荐摄入量（克）
        protein_calories = recommended_kcal * ratios['protein']
        fat_calories = recommended_kcal * ratios['fat']
        carbs_calories = recommended_kcal * ratios['carbs']

        protein_grams = protein_calories / CALORIES_PER_GRAM['protein']
        fat_grams = fat_calories / CALORIES_PER_GRAM['fat']
        carbs_grams = carbs_calories / CALORIES_PER_GRAM['carbs']

        return CalorieRecommendation(
            goal=user.goal.replace('_', ' ').title(), # e.g., 'lose_weight' -> 'Lose Weight'
            recommended_kcal=round(recommended_kcal, 2),
            protein_g=round(protein_grams, 2),
            fat_g=round(fat_grams, 2),
            carbs_g=round(carbs_grams, 2)
        )