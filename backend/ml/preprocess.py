"""数据清洗与多源融合（T-3）。

对 4 套原始数据做去重、缺失填充、异常值裁剪（winsorize），
输出清洗后的数据到 data/processed/，并统计可用样本量。
"""
import os

import pandas as pd

RAW = "data/raw"
PROCESSED = "data/processed"


def load():
    return {
        "meal_plan": pd.read_csv(f"{RAW}/meal_plan_exercise.csv"),
        "gym_members": pd.read_csv(f"{RAW}/gym_members_exercise_tracking.csv"),
        "survey": pd.read_csv(f"{RAW}/survey.csv"),
        "body_performance": pd.read_csv(f"{RAW}/body_performance.csv"),
    }


def clean(df, dedup=True):
    """缺失填充 + 异常值裁剪（可选去重），返回清洗后的 DataFrame 与原始行数。"""
    before = len(df)
    if dedup:
        df = df.drop_duplicates()

    num_cols = df.select_dtypes(include="number").columns
    # 数值列缺失值填中位数
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())
    # 分类/对象列缺失值填众数
    for col in df.select_dtypes(include="object").columns:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].mode().iloc[0])
    # 异常值裁剪：数值列按 1%/99% 分位数 winsorize（不减少样本量）
    for col in num_cols:
        lo, hi = df[col].quantile(0.01), df[col].quantile(0.99)
        df[col] = df[col].clip(lo, hi)

    return df, before


if __name__ == "__main__":
    os.makedirs(PROCESSED, exist_ok=True)
    total = 0
    for name, df in load().items():
        # MealPlan 为 16 个规则组合重复填充到 80k 的标签主数据集，训练时保留原始规模
        df_clean, before = clean(df, dedup=(name != "meal_plan"))
        df_clean.to_csv(f"{PROCESSED}/{name}_clean.csv", index=False, encoding="utf-8-sig")
        print(f"{name}: {before} -> {len(df_clean)}")
        total += len(df_clean)
    print("total usable samples:", total)
