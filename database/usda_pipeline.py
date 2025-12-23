import os
import sys
import utils


# 路径配置

DATA_DIR = "data"
USDA_DIR = "usda_csv"

FOUNDATION_FOOD_CSV = f"{USDA_DIR}/foundation_food/food.csv"
FOUNDATION_FOOD_NUTRIENT_CSV = f"{USDA_DIR}/foundation_food/food_nutrient.csv"
FOUNDATION_FOOD_PORTION_CSV = f"{USDA_DIR}/foundation_food/food_portion.csv"

FNDD_FOOD_CSV = f"{USDA_DIR}/fndd_food/food.csv"
FNDD_FOOD_NUTRIENT_CSV = f"{USDA_DIR}/fndd_food/food_nutrient.csv"
FNDD_FOOD_PORTION_CSV = f"{USDA_DIR}/fndd_food/food_portion.csv"

CLEAN_FOUNDATION = f"{DATA_DIR}/clean_foundation_food.csv"
CLEAN_FNDD = f"{DATA_DIR}/clean_fndd_food.csv"
CLEAN_FOOD = f"{DATA_DIR}/clean_food.csv"

FOOD_NAMES_TO_TRANSLATE = f"{DATA_DIR}/food_names_to_translate.csv"
FOOD_TRANSLATION = f"{DATA_DIR}/food_translation.csv"

CLEAN_WITH_ZH = f"{DATA_DIR}/clean_food_with_zh.csv"
CLEAN_DEDUP = f"{DATA_DIR}/clean_food_with_zh_dedup.csv"


# 营养素映射（与你 utils 一致）

SELECTED_NUTRIENTS = {
    1008: "energy_kcal",
    1003: "protein_g",
    1004: "fat_g",
    1005: "carbohydrate_g",
    1079: "fiber_total_dietary_g",
    2000: "sugars_g",
    1089: "fe_mg",
    1093: "na_mg",
}

FNDD_NUTRIENTS = {
    208: "energy_kcal",
    203: "protein_g",
    204: "fat_g",
    205: "carbohydrate_g",
    291: "fiber_total_dietary_g",
    269: "sugars_g",
    303: "fe_mg",
    307: "na_mg",
}

NUTRIENT_COLS = list(SELECTED_NUTRIENTS.values()) + ["serving_size_g"]


def step_1_clean_usda():
    print("\nStep 1: 清洗 USDA foundation / fndd 数据")

    utils.clean_food_dataset(
        FOUNDATION_FOOD_CSV,
        FOUNDATION_FOOD_NUTRIENT_CSV,
        FOUNDATION_FOOD_PORTION_CSV,
        SELECTED_NUTRIENTS,
        CLEAN_FOUNDATION
    )

    utils.clean_food_dataset(
        FNDD_FOOD_CSV,
        FNDD_FOOD_NUTRIENT_CSV,
        FNDD_FOOD_PORTION_CSV,
        FNDD_NUTRIENTS,
        CLEAN_FNDD
    )


def step_2_merge_sources():
    print("\nStep 2: 合并 foundation + fndd")

    utils.merge_food_sources(
        files=[
            (CLEAN_FOUNDATION, "foundation"),
            (CLEAN_FNDD, "fndd"),
        ],
        output_csv=CLEAN_FOOD
    )


def step_3_extract_food_names():
    print("\nStep 3: 提取待翻译食物名")

    utils.extract_unique_food_names(
        CLEAN_FOOD,
        FOOD_NAMES_TO_TRANSLATE
    )

    print("\n请完成翻译后再继续：")
    print(f"{FOOD_NAMES_TO_TRANSLATE} → {FOOD_TRANSLATION}")


def step_4_merge_translation():
    print("\nStep 4: 合并中英文")

    if not os.path.exists(FOOD_TRANSLATION):
        raise FileNotFoundError(
            f"❌ 未找到翻译文件：{FOOD_TRANSLATION}"
        )

    utils.merge_translation(
        CLEAN_FOOD,
        FOOD_TRANSLATION,
        CLEAN_WITH_ZH
    )


def step_5_dedup_by_zh():
    print("\nStep 5: 中文去重 + 非 0 平均")

    utils.dedup_by_chinese_name(
        CLEAN_WITH_ZH,
        CLEAN_DEDUP,
        nutrient_cols=NUTRIENT_COLS
    )

def step_6_load_to_db():
    print("\nStep 6: 导入数据库")

    utils.load_foods_to_database(
        CLEAN_DEDUP
    )

def main():
    print("\n启动食品营养数据 Pipeline\n")

    os.makedirs(DATA_DIR, exist_ok=True)

    step_1_clean_usda()
    step_2_merge_sources()
    step_3_extract_food_names()

    print("\nPipeline 暂停在翻译阶段")
    print("完成翻译后，重新运行 pipeline.py 即可继续\n")

    step_4_merge_translation()
    step_5_dedup_by_zh()

    print("\nPipeline 全部完成！")
    print(f"最终文件：{CLEAN_DEDUP}")




if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\nPipeline 失败")
        print(e)
        sys.exit(1)