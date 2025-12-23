import logging
import os
import re
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np
from typing import Dict, List


logging.basicConfig(level=logging.INFO)
DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/nutri_plan"
engine = create_engine(DATABASE_URL)


def mean_ignore_zero(series: pd.Series) -> float:
    """只对非 0 数值求平均"""
    s = pd.to_numeric(series, errors="coerce")
    s = s.dropna()
    s = s[s != 0]
    if len(s) == 0:
        return 0.0
    return float(s.mean())


def normalize_text(text: str) -> str:
    """
    统一英文描述规范化：
    - 去引号
    - 小写
    - 多空格压缩
    """
    if pd.isna(text):
        return ""
    text = str(text).strip()
    text = text.strip('"').strip("'")
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text


def clean_food_dataset(
    food_csv: str,
    nutrient_csv: str,
    portion_csv: str | None,
    nutrient_map: Dict[int, str],
    output_csv: str
):
    """清洗 USDA food + nutrient 数据"""
    food_df = pd.read_csv(food_csv, low_memory=False)
    nutrient_df = pd.read_csv(nutrient_csv, low_memory=False)

    food_df = food_df[["fdc_id", "description"]]

    nutrient_df = nutrient_df[nutrient_df["nutrient_id"].isin(nutrient_map)]
    nutrient_df["nutrient_name"] = nutrient_df["nutrient_id"].map(nutrient_map)

    nutrient_pivot = (
        nutrient_df
        .pivot_table(
            index="fdc_id",
            columns="nutrient_name",
            values="amount",
            aggfunc="mean"
        )
        .reset_index()
    )

    merged = food_df.merge(nutrient_pivot, on="fdc_id", how="left")

    if portion_csv:
        portion_df = pd.read_csv(portion_csv, low_memory=False)
        portion_avg = (
            portion_df[["fdc_id", "gram_weight"]]
            .groupby("fdc_id", as_index=False)
            .mean()
            .rename(columns={"gram_weight": "serving_size_g"})
        )
        merged = merged.merge(portion_avg, on="fdc_id", how="left")
    else:
        merged["serving_size_g"] = 100.0

    value_cols = list(nutrient_map.values()) + ["serving_size_g"]

    final_df = (
        merged
        .groupby("description", as_index=False)[value_cols]
        .mean()
        .fillna(0)
    )

    final_df.to_csv(output_csv, index=False)
    print(f"✅ Saved → {output_csv}")


def merge_food_sources(files: List[tuple], output_csv: str):
    """合并 foundation / fndd 数据"""
    dfs = []

    REQUIRED_COLS = [
        "description",
        "energy_kcal",
        "protein_g",
        "fat_g",
        "carbohydrate_g",
        "fiber_total_dietary_g",
        "sugars_g",
        "fe_mg",
        "na_mg",
        "serving_size_g",
    ]

    for file, source in files:
        df = pd.read_csv(file)
        for col in REQUIRED_COLS:
            if col not in df.columns:
                df[col] = 0
        df = df[REQUIRED_COLS]
        df["source"] = source
        dfs.append(df)

    final_df = pd.concat(dfs, ignore_index=True)
    final_df = final_df.rename(columns={"description": "description_en"})
    final_df.to_csv(output_csv, index=False)
    print(f"✅ 合并完成 → {output_csv}")


def extract_unique_food_names(input_csv: str, output_csv: str):
    """提取唯一英文食物名"""
    df = pd.read_csv(input_csv)
    unique_names = (
        df[["description_en"]]
        .drop_duplicates()
        .sort_values("description_en")
    )
    unique_names.to_csv(output_csv, index=False)
    print(f"✅ 已生成 {output_csv}")


def merge_translation(
    food_csv: str,
    translation_csv: str,
    output_csv: str
):
    """合并中英文描述"""
    food_df = pd.read_csv(food_csv)
    trans_df = pd.read_csv(translation_csv)

    food_df["key"] = food_df["description_en"].apply(normalize_text)
    trans_df["key"] = trans_df["description_en"].apply(normalize_text)

    trans_df = trans_df.drop_duplicates("key")

    merged = food_df.merge(
        trans_df[["key", "description_zh"]],
        on="key",
        how="left"
    ).drop(columns=["key"])

    merged.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"✅ 合并完成 → {output_csv}")


def dedup_by_chinese_name(
    input_csv: str,
    output_csv: str,
    nutrient_cols: List[str]
):
    df = pd.read_csv(input_csv)

    for col in nutrient_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    result = (
        df
        .groupby("description_zh", as_index=False)
        .agg({
            **{col: mean_ignore_zero for col in nutrient_cols},
            "description_en": "first",
            "source": "first"
        })
    )

    result.to_csv(output_csv, index=False)
    print(f"✅ 去重完成 → {output_csv}")

def import_foods(food_csv):

    df = pd.read_csv(
        food_csv,
        usecols=["description_zh", "energy_kcal", "protein_g", "fat_g", "carbohydrate_g", "fiber_total_dietary_g", "sugars_g", "fe_mg", "na_mg", "serving_size_g", "description_en", "source"]
    )

    logging.info(f"导入 food：{len(df)} 条")

    df.to_sql(
        "foods_information",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000
    )