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
        usecols=["description_zh", "energy_kcal", "protein_g", "fat_g", "carbohydrate_g", "fiber_total_dietary_g", "sugars_g", "fe_mg", "na_mg", "serving_size_g", "description_en", "source"]
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



def main():
    import_foods("./data/clean_food_with_zh_dedup.csv")

if __name__ == "__main__":
    main()