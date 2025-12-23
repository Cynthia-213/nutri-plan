import pandas as pd
from sqlalchemy import create_engine

# 数据库配置
DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/nutri_plan"
engine = create_engine(DATABASE_URL)

def import_with_averaging(file_path):
    df = pd.read_excel(file_path)
    df.columns = [col.replace('\n', '').strip() for col in df.columns]
    
    column_mapping = {
        '食物（每100克）': 'description_zh',
        '能量（kal）': 'energy_kcal',
        '蛋白质（克）': 'protein_g',
        '糖类（克）': 'carbohydrate_g',
        '脂肪（克）': 'fat_g',
        '纤维（克）': 'fiber_total_dietary_g',
        '钠（毫克）': 'na_mg',
        '铁（毫克）': 'fe_mg'
    }
    
    valid_cols = [c for c in column_mapping.keys() if c in df.columns]
    df_mapped = df[valid_cols].rename(columns=column_mapping)
    
    numeric_cols = ['energy_kcal', 'protein_g', 'fat_g', 'carbohydrate_g', 
                    'fiber_total_dietary_g', 'na_mg', 'fe_mg']
    
    for col in numeric_cols:
        df_mapped[col] = pd.to_numeric(df_mapped[col].replace('-', None), errors='coerce')

    print("正在计算同名食物的营养平均值...")
    df_avg = df_mapped.groupby('description_zh', as_index=False)[numeric_cols].mean()
    
    df_avg['source'] = 'CDC China'
    df_avg['serving_size_g'] = 100.00
    df_avg['sugars_g'] = 0
    df_avg['description_en'] = None
    

    try:
        df_avg.to_sql('foods', con=engine, if_exists='append', index=False)
        print(f"成功导入 {len(df_avg)} 条聚合后的食物数据！")
    except Exception as e:
        print(f"❌ 导入失败: {e}")

if __name__ == "__main__":
    import_with_averaging('./data/中国食物营养成分表.xlsx')