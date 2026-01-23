import random
from typing import Dict, List, Any
from sqlalchemy import text
from app.crud.crud_food import food
from app.core.config import settings
import zhipuai

ratios = {
    'gain_muscle': {'protein': 80, 'carbs': 30, 'veg': 40},
    'lose_weight': {'protein': 60, 'carbs': 20, 'veg': 70},
    'maintain': {'protein': 50, 'carbs': 50, 'veg': 50}
}

class MenuGeneratorService:
    @staticmethod
    def generate_menu(db, current_user, target_calories: float, target_protein: float, target_fat: float, target_carbs: float) -> Dict[str, Any]:
        # 调用刚才写的 CRUD 方法，传入 user_id 以排除禁止的食物
        candidate_list = food.get_ai_candidates(db, preference=current_user.goal, user_id=current_user.id)
        
        # 极简化数据：只给 AI 必要的字段，节省 Token
        compact_foods = []
        for f in candidate_list:
            compact_foods.append({
                "id": f.id,
                "name": f.description_zh,
                "kcal": float(f.energy_kcal),
                "p": float(f.protein_g),
                "f": float(f.fat_g),
                "c": float(f.carbohydrate_g),
                "tags": [t for t, v in {
                    "高蛋白": f.is_high_protein,
                    "低碳": f.is_low_carb,
                    "高纤": f.is_high_fiber
                }.items() if v]
            })

        # 构造 Prompt
        prompt = f"""
            你是一名专业营养师 + 营养配餐系统。

            你的任务是：**从给定候选食物池中，组合出一份【三餐制】的每日菜单**，
            使其尽可能满足用户的营养目标与热量约束。

            ====================
            【用户目标】
            - 每日目标热量：{target_calories} kcal
            - 每日目标蛋白质：{target_protein} g
            - 每日目标脂肪：{target_fat} g
            - 每日目标碳水：{target_carbs} g
            - 饮食偏好 / 目标：{current_user.goal}

            ====================
            【候选食物池（只能使用这些，不得新增）】
            以下是 JSON 数组，每个元素代表一种食物：
            {compact_foods}

            字段说明：
            - id: 食物唯一标识（必须原样返回）
            - name: 食物名称
            - kcal: 每 100g 热量
            - p / f / c: 每 100g 蛋白质 / 脂肪 / 碳水（克）
            - tags: 食物标签（如 高蛋白 / 低碳 / 高纤）

            ====================
            【强制规则（必须遵守）】
            1. 【只能】从候选食物池中选择食物，禁止虚构或改写 id。
            2. 每餐必须至少包含 1 种食物。
            3. 每种食物的 grams 必须为 10 的倍数，且 >= 50g。
            4. 每种食物在一天内最多出现 2 次（可跨餐）。
            5. 全天总热量必须满足：
            {target_calories - 50} <= total_kcal <= {target_calories + 50}
            6. 尽量贴近蛋白质 / 脂肪 / 碳水目标（允许轻微偏差）。

            ====================
            【输出格式（严格 JSON，不要任何解释文本）】
            {{
            "meals": [
                {{
                "name": "早餐",
                "items": [
                    {{
                    "id": <int>,
                    "grams": <int>,
                    "kcal": <float>
                    }}
                ],
                "meal_kcal": <float>
                }},
                {{
                "name": "午餐",
                "items": [...],
                "meal_kcal": <float>
                }},
                {{
                "name": "晚餐",
                "items": [...],
                "meal_kcal": <float>
                }}
            ],
            "summary": {{
                "total_kcal": <float>,
                "total_protein": <float>,
                "total_fat": <float>,
                "total_carbs": <float>
            }}
            }}

            注意：
            - kcal / 营养素请根据 grams 与每 100g 数值计算
            - 不要输出 Markdown
            - 不要输出解释性文字
            - JSON 必须可被程序直接解析
            """
        
        client = zhipuai.ZhipuAI(api_key=settings.ZHIPU_API_KEY)
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        
        if response.choices:
            return response.choices[0].message.content.strip()

    @staticmethod 
    def verify_and_correct_menu(db, ai_json):
        meals = ai_json.get("meals", [])
        total_stats = {"kcal": 0, "p": 0, "f": 0, "c": 0}
        
        for meal in meals:
            meal_kcal = 0
            for item in meal.get("items", []):
                # 1. 强制重新从数据库获取精准数据
                db_food = food.get_food_by_id(db, food_id=item['id'])
                if not db_food:
                    continue
                    
                # 2. 按照 AI 给出的重量重新计算真实数值
                ratio = item['grams'] / 100.0
                true_kcal = float(db_food.energy_kcal) * ratio
                true_p = float(db_food.protein_g) * ratio
                true_f = float(db_food.fat_g) * ratio
                true_c = float(db_food.carbohydrate_g) * ratio
                
                # 3. 修正 item 中的数值（防止 AI 算错）
                item['kcal'] = round(true_kcal, 1)
                
                # 累加
                meal_kcal += true_kcal
                total_stats['kcal'] += true_kcal
                total_stats['p'] += true_p
                total_stats['f'] += true_f
                total_stats['c'] += true_c
                
            meal['meal_kcal'] = round(meal_kcal, 1)
    
            # 更新总计
            ai_json['summary'] = {
                "total_kcal": round(total_stats['kcal'], 1),
                "total_protein": round(total_stats['p'], 1),
                "total_fat": round(total_stats['f'], 1),
                "total_carbs": round(total_stats['c'], 1)
            }
            return ai_json
    @staticmethod
    def is_kcal_valid(summary, target_kcal):
        # 允许 5% 或 100kcal 的固定误差
        diff = abs(summary['total_kcal'] - target_kcal)
        return diff <= 100
        
# 创建一个实例以便全局使用
menu_generator = MenuGeneratorService()