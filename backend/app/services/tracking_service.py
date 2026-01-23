from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import date
import zhipuai
from app.core.config import settings
import logging
from collections import defaultdict

from app.crud.crud_log import log
from app.crud.crud_food import food
from app.crud.crud_exercise import exercise
from app.models.user import User
from app.schemas import log as log_schema
from app.services.calorie_calculator import CalorieCalculatorService
from app.services.recommendation_service import RecommendationService

class TrackingService:
    def get_daily_summary(self, db: Session, user: User, log_date: date) -> log_schema.DailySummary:
        # 获取指定日期的食物和运动日志
        food_logs = log.get_food_logs_by_user_and_date(db, user_id=user.id, log_date=log_date)
        exercise_logs = log.get_exercise_logs_by_user_and_date(db, user_id=user.id, log_date=log_date)

        # 计算总摄入
        total_intake_kcal = 0
        total_protein_g = 0
        total_fat_g = 0
        total_carbs_g = 0
        detailed_food_log = []

        for cur_log in food_logs:
            cur_food = food.get_food_by_id(db, food_id=cur_log.food_id)
            if cur_food:
                ratio = float(cur_log.serving_grams) / 100
                
                cals = float(cur_log.total_calories) if cur_log.total_calories is not None else float(cur_food.energy_kcal) * ratio
                prot = float(cur_food.protein_g) * ratio
                fat = float(cur_food.fat_g) * ratio
                carb = float(cur_food.carbohydrate_g) * ratio

                total_intake_kcal += cals
                total_protein_g += prot
                total_fat_g += fat
                total_carbs_g += carb
                
                detailed_food_log.append(log_schema.LoggedFoodItem(
                    food=cur_food,
                    serving_grams=cur_log.serving_grams,
                    meal_type=cur_log.meal_type,
                    total_calories=round(cals, 2),
                    total_protein=round(prot, 2),
                    total_fat=round(fat, 2),
                    total_carbs=round(carb, 2),
                ))

        bmr = CalorieCalculatorService.get_user_bmr(user)
        tdee = CalorieCalculatorService.get_user_tdee(user)
        
        # 计算总消耗
        total_exercise_burned = 0
        detailed_exercise_log = []
        
        for cur_log in exercise_logs:
            cur_exercise = exercise.get_exercise_by_id(db, exercise_id=cur_log.exercise_id)
            if cur_exercise:
                burned = float(cur_log.calories_burned) if cur_log.calories_burned is not None else CalorieCalculatorService.get_exercise_calories(
                    met_value=float(cur_exercise.met_value),
                    weight_kg=float(user.weight_kg),
                    duration_minutes=cur_log.duration_minutes
                )
                total_exercise_burned += burned
                detailed_exercise_log.append(log_schema.LoggedExerciseItem(
                    exercise_name=cur_exercise.name,
                    duration_minutes=cur_log.duration_minutes,
                    calories_burned=round(burned, 2)
                ))
        
        total_burned_kcal = bmr + total_exercise_burned

        # 计算净热量
        net_calories = total_intake_kcal - total_burned_kcal

        # 获取推荐值
        recommendations = RecommendationService.get_calorie_recommendation(user)

        # 构建并返回每日总结（不再包含AI建议）
        return log_schema.DailySummary(
            log_date=log_date,
            bmr=round(bmr, 2),
            tdee=round(tdee, 2),
            total_intake_kcal=round(total_intake_kcal, 2),
            total_exercise_burned=round(total_exercise_burned, 2),
            total_burned_kcal=round(total_burned_kcal, 2),
            net_calories=round(net_calories, 2),
            total_protein_g=round(total_protein_g, 2),
            total_fat_g=round(total_fat_g, 2),
            total_carbs_g=round(total_carbs_g, 2),
            food_log=detailed_food_log,
            exercise_log=detailed_exercise_log,
            recommended_daily_kcal=recommendations.recommended_kcal,
            recommended_protein_g=recommendations.protein_g,
            recommended_fat_g=recommendations.fat_g,
            recommended_carbs_g=recommendations.carbs_g,
            ai_summary=None
        )
    
    def generate_ai_summary(self, db: Session, user: User, log_date: date) -> str:
        """
        生成AI健康建议（独立方法）
        """
        # 获取指定日期的食物和运动日志
        food_logs = log.get_food_logs_by_user_and_date(db, user_id=user.id, log_date=log_date)
        exercise_logs = log.get_exercise_logs_by_user_and_date(db, user_id=user.id, log_date=log_date)

        # 计算总摄入
        total_intake_kcal = 0
        total_protein_g = 0
        total_fat_g = 0
        total_carbs_g = 0

        for cur_log in food_logs:
            cur_food = food.get_food_by_id(db, food_id=cur_log.food_id)
            if cur_food:
                ratio = float(cur_log.serving_grams) / 100
                total_intake_kcal += float(cur_log.total_calories) if cur_log.total_calories is not None else float(cur_food.energy_kcal) * ratio
                total_protein_g += float(cur_food.protein_g) * ratio
                total_fat_g += float(cur_food.fat_g) * ratio
                total_carbs_g += float(cur_food.carbohydrate_g) * ratio

        bmr = CalorieCalculatorService.get_user_bmr(user)
        tdee = CalorieCalculatorService.get_user_tdee(user)
        
        # 计算总消耗
        total_exercise_burned = 0
        for cur_log in exercise_logs:
            cur_exercise = exercise.get_exercise_by_id(db, exercise_id=cur_log.exercise_id)
            if cur_exercise:
                burned = CalorieCalculatorService.get_exercise_calories(
                    met_value=float(cur_exercise.met_value),
                    weight_kg=float(user.weight_kg),
                    duration_minutes=cur_log.duration_minutes
                )
                total_exercise_burned += burned
        
        total_burned_kcal = bmr + total_exercise_burned
        net_calories = total_intake_kcal - total_burned_kcal

        # 获取推荐值
        recommendations = RecommendationService.get_calorie_recommendation(user)
        
        # 生成AI建议
        ai_summary = None
        if settings.ZHIPU_API_KEY:
            try:
                client = zhipuai.ZhipuAI(api_key=settings.ZHIPU_API_KEY)
                
                prompt = f"""
                你是一个专业的健康运动和营养顾问。请根据以下用户的每日数据，为他/她生成一份简洁、友好、鼓励性的每日健康总结。
                总结应包括饮食和运动两方面，指出做得好的地方，并提供两三个具体的、可行的优化建议。

                用户数据如下：
                - 日期: {log_date}
                - 用户目标： {user.goal.replace('_', ' ').title()}
                - 基础代谢率 (BMR): {bmr:.0f} 大卡
                - 总每日消耗 (TDEE): {tdee:.0f} 大卡
                - 推荐每日摄入热量: {recommendations.recommended_kcal:.0f} 大卡
                - 实际总摄入热量: {total_intake_kcal:.0f} 大卡
                - 运动总消耗热量: {total_burned_kcal:.0f} 大卡
                - 净热量（摄入-消耗）: {net_calories:.0f} 大卡

                - 宏量营养素摄入:
                - 蛋白质: {total_protein_g:.1f} 克 (推荐: {recommendations.protein_g:.1f} 克)
                - 脂肪: {total_fat_g:.1f} 克 (推荐: {recommendations.fat_g:.1f} 克)
                - 碳水化合物: {total_carbs_g:.1f} 克 (推荐: {recommendations.carbs_g:.1f} 克)
                
                - 饮食记录: {', '.join([f'{(log.food.description_zh if log.food and log.food.description_zh else log.food.description_en if log.food else "未知食物")}({log.serving_grams}克)' for log in food_logs]) if food_logs else '无'}
                - 运动记录: {', '.join([f'{log.exercise.name if log.exercise else "未知运动"}({log.duration_minutes}分钟)' for log in exercise_logs]) if exercise_logs else '无'}

                请根据以上信息，生成一段大约400字的总结和建议。
                """
                
                response = client.chat.completions.create(
                    model="glm-4.7",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                )
                
                if response.choices:
                    ai_summary = response.choices[0].message.content.strip()

            except Exception as e:
                logging.error(f"AI summary generation failed: {e}")
                ai_summary = "无法生成AI建议，请稍后再试。"
        else:
            ai_summary = "AI服务未配置，无法生成建议。"
        
        return ai_summary

    def get_energy_summary(self, db: Session, user: User, period_type: str, energy_type: str, start_date: date, end_date: date) -> log_schema.EnergySummary:
        bmr = CalorieCalculatorService.get_user_bmr(user)
        
        summary_data = defaultdict(float)

        if energy_type == "intake":
            logs = log.get_food_logs_by_user_and_date_range(db, user_id=user.id, start_date=start_date, end_date=end_date)
            for cur_log in logs:
                if cur_log.food:
                    ratio = float(cur_log.serving_grams) / 100
                    cals = float(cur_log.food.energy_kcal) * ratio
                    if period_type == "daily":
                        period_key = cur_log.log_date.strftime("%Y-%m-%d")
                    elif period_type == "monthly":
                        period_key = cur_log.log_date.strftime("%Y-%m")
                    summary_data[period_key] += cals
        
        elif energy_type == "expenditure":
            logs = log.get_exercise_logs_by_user_and_date_range(db, user_id=user.id, start_date=start_date, end_date=end_date)
            for cur_log in logs:
                if cur_log.exercise:
                    burned = CalorieCalculatorService.get_exercise_calories(
                        met_value=float(cur_log.exercise.met_value),
                        weight_kg=float(user.weight_kg),
                        duration_minutes=cur_log.duration_minutes
                    )
                    if period_type == "daily":
                        period_key = cur_log.log_date.strftime("%Y-%m-%d")
                    elif period_type == "monthly":
                        period_key = cur_log.log_date.strftime("%Y-%m")
                    else:
                        period_key = cur_log.log_date.strftime("%Y")
                    summary_data[period_key] += burned

        sorted_periods = sorted(summary_data.keys())
        
        response_data = [
            log_schema.EnergySummaryItem(
                period=p,
                total_calories=round(summary_data[p], 2)
            ) for p in sorted_periods
        ]
        
        return log_schema.EnergySummary(data=response_data, bmr=bmr)

tracking_service = TrackingService()