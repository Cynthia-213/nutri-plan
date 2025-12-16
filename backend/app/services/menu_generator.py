import random
from typing import Dict, List, Any

# # 在真实应用中，这可以是从数据库中根据特定条件（如健康、低脂）查询得到的食物列表
# SIMULATED_FOOD_DB = {
#     'protein_sources': [
#         {'name': '鸡胸肉', 'calories_per_100g': 165, 'protein': 31, 'fat': 3.6, 'carbs': 0},
#         {'name': '三文鱼', 'calories_per_100g': 208, 'protein': 20, 'fat': 13, 'carbs': 0},
#         {'name': '鸡蛋', 'calories_per_100g': 155, 'protein': 13, 'fat': 11, 'carbs': 1.1},
#         {'name': '豆腐', 'calories_per_100g': 76, 'protein': 8, 'fat': 5, 'carbs': 2},
#         {'name': '希腊酸奶', 'calories_per_100g': 59, 'protein': 10, 'fat': 0.4, 'carbs': 3.6},
#     ],
#     'carb_sources': [
#         {'name': '糙米', 'calories_per_100g': 111, 'protein': 2.6, 'fat': 0.9, 'carbs': 23},
#         {'name': '燕麦片', 'calories_per_100g': 389, 'protein': 16.9, 'fat': 6.9, 'carbs': 66},
#         {'name': '红薯', 'calories_per_100g': 86, 'protein': 1.6, 'fat': 0.1, 'carbs': 20},
#         {'name': '全麦面包', 'calories_per_100g': 247, 'protein': 13, 'fat': 3.4, 'carbs': 41},
#         {'name': '藜麦', 'calories_per_100g': 120, 'protein': 4.1, 'fat': 1.9, 'carbs': 21},
#     ],
#     'fat_sources': [
#         {'name': '牛油果', 'calories_per_100g': 160, 'protein': 2, 'fat': 15, 'carbs': 9},
#         {'name': '杏仁', 'calories_per_100g': 579, 'protein': 21, 'fat': 49, 'carbs': 22},
#         {'name': '橄榄油', 'calories_per_100g': 884, 'protein': 0, 'fat': 100, 'carbs': 0},
#     ],
#     'vegetables': [
#         {'name': '西兰花', 'calories_per_100g': 34, 'protein': 2.8, 'fat': 0.4, 'carbs': 7},
#         {'name': '菠菜', 'calories_per_100g': 23, 'protein': 2.9, 'fat': 0.4, 'carbs': 3.6},
#         {'name': '番茄', 'calories_per_100g': 18, 'protein': 0.9, 'fat': 0.2, 'carbs': 3.9},
#         {'name': '胡萝卜', 'calories_per_100g': 41, 'protein': 0.9, 'fat': 0.2, 'carbs': 10},
#     ]
# }

class MenuGeneratorService:
    """
    一个“伪AI”菜单生成器
    它通过组合预定义的食物来尝试满足用户的热量和宏量营养素目标
    """
    @staticmethod
    def generate_menu(target_calories: float, target_protein: float, target_fat: float, target_carbs: float) -> Dict[str, Any]:
        """
        生成一天的三餐菜单
        
        这是一个非常简化的模拟，它会随机选择食物，并估算份量
        """
        menu = {
            "breakfast": [],
            "lunch": [],
            "dinner": [],
            "totals": {
                "calories": 0, "protein": 0, "fat": 0, "carbs": 0
            }
        }
        
        # 简化逻辑：为每餐随机选择食物
        
        # 早餐: 碳水 + 蛋白质
        breakfast_carb = random.choice(SIMULATED_FOOD_DB['carb_sources'])
        breakfast_protein = random.choice(SIMULATED_FOOD_DB['protein_sources'])
        menu['breakfast'].extend([f"1份 {breakfast_carb['name']}", f"1份 {breakfast_protein['name']}"])

        # 午餐: 蛋白质 + 碳水 + 蔬菜
        lunch_protein = random.choice(SIMULATED_FOOD_DB['protein_sources'])
        lunch_carb = random.choice(SIMULATED_FOOD_DB['carb_sources'])
        lunch_veg = random.choice(SIMULATED_FOOD_DB['vegetables'])
        menu['lunch'].extend([f"1.5份 {lunch_protein['name']}", f"1份 {lunch_carb['name']}", f"1份 {lunch_veg['name']}"])

        # 晚餐: 蛋白质 + 蔬菜 + 少量脂肪
        dinner_protein = random.choice(SIMULATED_FOOD_DB['protein_sources'])
        dinner_veg = random.choice(SIMULATED_FOOD_DB['vegetables'])
        dinner_fat = random.choice(SIMULATED_FOOD_DB['fat_sources'])
        menu['dinner'].extend([f"1份 {dinner_protein['name']}", f"2份 {dinner_veg['name']}", f"0.5份 {dinner_fat['name']}"])
        
        # 这是一个非常粗略的估算，真实应用需要更复杂的算法来匹配目标
        # 这里我们只返回一个示意的菜单结构和文字描述
        
        return {
            "target_goals": {
                "calories": round(target_calories),
                "protein_g": round(target_protein),
                "fat_g": round(target_fat),
                "carbs_g": round(target_carbs),
            },
            "suggested_menu": menu,
            "disclaimer": "这是一个由AI模拟生成的示例菜单。份量和具体食物需要根据您的实际情况进行调整。建议咨询专业营养师。"
        }
        
# 创建一个实例以便全局使用
menu_generator = MenuGeneratorService()