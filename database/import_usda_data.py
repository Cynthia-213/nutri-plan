import pandas as pd
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)

DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/nutri_plan"
engine = create_engine(DATABASE_URL)

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

def import_foods(food_csv):
    df = pd.read_csv(
        food_csv,
        usecols=["fdc_id", "data_type", "description", "food_category_id"]
    )

    logging.info(f"导入 food：{len(df)} 条")

    df.to_sql(
        "foods",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000
    )

def import_nutrient(nutrient_csv):
    df = pd.read_csv(
        nutrient_csv,
        usecols=["id", "name", "unit_name"]
    )

    df = df[df["id"].isin(SELECTED_NUTRIENTS.keys())]

    logging.info(f"导入 nutrient：{len(df)} 条")

    df.to_sql(
        "nutrient",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000
    )

def import_food_nutrient(food_nutrient_csv):
    df = pd.read_csv(
        food_nutrient_csv,
        usecols=["fdc_id", "nutrient_id", "amount"]
    )
    df = df[df["nutrient_id"].isin(SELECTED_NUTRIENTS.keys())]

    logging.info(f"导入 nutrient：{len(df)} 条")

    df.to_sql(
        "food_nutrient",
        engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=1000
    )


def import_food_portion(portion_csv):
    df = pd.read_csv(
        portion_csv,
        usecols=["fdc_id", "gram_weight"]
    )

    df = df.dropna(subset=["gram_weight"])
    df = df[df["gram_weight"] > 0]

    portion_df = (
        df
        .groupby("fdc_id", as_index=False)
        .agg(gram_weight=("gram_weight", "median"))
    )

    logging.info(f"聚合后 portion 记录数（1 food = 1 portion）：{len(portion_df)}")


    portion_df.to_sql(
        "food_portion",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000
    )

def import_food_category(csv_path):
    df = pd.read_csv(
        csv_path,
        usecols=["id", "description"]
    )

    logging.info(f"导入 food_category：{len(df)} 条")

    df.to_sql(
        "food_category",
        engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=1000
    )

def main():
    import_foods("./usda_csv/food.csv")
    import_nutrient("./usda_csv/nutrient.csv")
    import_food_nutrient("./usda_csv/food_nutrient.csv")
    import_food_portion("./usda_csv/food_portion.csv")
    import_food_category("./usda_csv/food_category.csv")

if __name__ == "__main__":
    main()