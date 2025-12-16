from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import date
import zhipuai
from app.core.config import settings
import logging

from app.crud.crud_log import log_crud
from app.crud.crud_food import food_crud
from app.models.user import User
from app.schemas import log as log_schema
from app.services.calorie_calculator import CalorieCalculatorService
from app.services.recommendation_service import RecommendationService

class TrackingService:
    def get_daily_summary(self, db: Session, user: User, log_date: date) -> log_schema.DailySummary:
        # 获取指定日期的食物和运动日志
        food_logs = log_crud.get_food_logs_by_user_and_date(db, user_id=user.id, log_date=log_date)
        exercise_logs = log_crud.get_exercise_logs_by_user_and_date(db, user_id=user.id, log_date=log_date)

        # 计算总摄入
        total_intake_kcal = 0
        total_protein_g = 0
        total_fat_g = 0
        total_carbs_g = 0
        detailed_food_log = []

        for log in food_logs:
            food = food_crud.get_food_by_id(db, food_id=log.food_id)
            if food:
                ratio = float(log.serving_grams) / 100
                
                cals = float(food.energy_kcal) * ratio
                prot = float(food.protein_g) * ratio
                fat = float(food.fat_g) * ratio
                carb = float(food.carbohydrate_g) * ratio
                
                total_intake_kcal += cals
                total_protein_g += prot
                total_fat_g += fat
                total_carbs_g += carb
                
                detailed_food_log.append(log_schema.LoggedFoodItem(
                    food=food,
                    serving_grams=log.serving_grams,
                    total_calories=round(cals, 2),
                    total_protein=round(prot, 2),
                    total_fat=round(fat, 2),
                    total_carbs=round(carb, 2),
                ))

        # 计算总消耗
        bmr = CalorieCalculatorService.get_user_bmr(user)
        
        total_exercise_burned = 0
        detailed_exercise_log = []
        
        for log in exercise_logs:
            exercise = food_crud.get_exercise_by_id(db, exercise_id=log.exercise_id)
            if exercise:
                burned = CalorieCalculatorService.get_exercise_calories(
                    met_value=float(exercise.met_value),
                    weight_kg=float(user.weight_kg),
                    duration_minutes=log.duration_minutes
                )
                total_exercise_burned += burned
                detailed_exercise_log.append(log_schema.LoggedExerciseItem(
                    exercise_name=exercise.name,
                    duration_minutes=log.duration_minutes,
                    calories_burned=round(burned, 2)
                ))
        
        total_burned_kcal = bmr + total_exercise_burned

        # 计算净热量
        net_calories = total_intake_kcal - total_burned_kcal

        # 获取推荐值
        recommendations = RecommendationService.get_calorie_recommendation(user)

        if settings.ZHIPU_API_KEY:
            try:
                client = zhipuai.ZhipuAI(api_key=settings.ZHIPU_API_KEY)
                
                prompt = f"""
                你是一个专业的健康和营养顾问。请根据以下用户的每日数据，为他/她生成一份简洁、友好、鼓励性的每日健康总结。
                总结应包括饮食和运动两方面，指出做得好的地方，并提供一两个具体的、可行的优化建议。

                用户数据如下：
                - 日期: {log_date}
                - 用户目标： {user.goal.replace('_', ' ').title()}
                - 推荐每日摄入热量: {recommendations.recommended_kcal:.0f} 大卡
                - 实际总摄入热量: {total_intake_kcal:.0f} 大卡
                - 运动总消耗热量: {total_burned_kcal:.0f} 大卡
                - 净热量（摄入-消耗）: {net_calories:.0f} 大卡

                - 宏量营养素摄入:
                - 蛋白质: {total_protein_g:.1f} 克 (推荐: {recommendations.protein_g:.1f} 克)
                - 脂肪: {total_fat_g:.1f} 克 (推荐: {recommendations.fat_g:.1f} 克)
                - 碳水化合物: {total_carbs_g:.1f} 克 (推荐: {recommendations.carbs_g:.1f} 克)
                
                - 饮食记录: {', '.join([f'{item.food.description}({item.serving_grams}克)' for item in food_logs]) if food_logs else '无'}
                - 运动记录: {', '.join([f'{item.exercise.name}({item.duration_minutes}分钟)' for item in exercise_logs]) if exercise_logs else '无'}

                请根据以上信息，生成一段大约200-250字的总结和建议。
                """
                
                response = client.chat.completions.create(
                    model="glm-3-turbo",
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

        # 构建并返回每日总结
        return log_schema.DailySummary(
            log_date=log_date,
            bmr=round(bmr, 2),
            total_intake_kcal=round(total_intake_kcal, 2),
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
            ai_summary=ai_summary
        )

    def get_energy_summary(self, db: Session, user: User, period_type: str, energy_type: str, start_date: date, end_date: date) -> log_schema.EnergySummary:
        from collections import defaultdict
        
        summary_data = defaultdict(float)

        if energy_type == "intake":
            logs = log_crud.get_food_logs_by_user_and_date_range(db, user_id=user.id, start_date=start_date, end_date=end_date)
            for log in logs:
                if log.food:
                    ratio = float(log.serving_grams) / 100
                    cals = float(log.food.energy_kcal) * ratio
                    if period_type == "daily":
                        period_key = log.log_date.strftime("%Y-%m-%d")
                    elif period_type == "monthly":
                        period_key = log.log_date.strftime("%Y-%m")
                    else: # yearly
                        period_key = log.log_date.strftime("%Y")
                    summary_data[period_key] += cals
        
        elif energy_type == "expenditure":
            logs = log_crud.get_exercise_logs_by_user_and_date_range(db, user_id=user.id, start_date=start_date, end_date=end_date)
            for log in logs:
                if log.exercise:
                    burned = CalorieCalculatorService.get_exercise_calories(
                        met_value=float(log.exercise.met_value),
                        weight_kg=float(user.weight_kg),
                        duration_minutes=log.duration_minutes
                    )
                    if period_type == "daily":
                        period_key = log.log_date.strftime("%Y-%m-%d")
                    elif period_type == "monthly":
                        period_key = log.log_date.strftime("%Y-%m")
                    else: # yearly
                        period_key = log.log_date.strftime("%Y")
                    summary_data[period_key] += burned

        # Sort by period and format for response
        sorted_periods = sorted(summary_data.keys())
        
        response_data = [
            log_schema.EnergySummaryItem(
                period=p,
                total_calories=round(summary_data[p], 2)
            ) for p in sorted_periods
        ]
        
        return log_schema.EnergySummary(data=response_data)

tracking_service = TrackingService()