"""生成模拟问卷数据与 Body Performance 占位数据（T-2）。

说明：
- survey.csv：模拟问卷星导出的本土化样本（9 个输入特征）。
- body_performance.csv：占位数据，正式数据需从 Kaggle
  kukuroo3/body-performance-data 下载（当前网络无法直连 Kaggle）。
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)


def make_survey(n=500):
    goals = ["减脂", "增肌", "塑形", "提升耐力", "保持健康"]
    exps = ["新手", "初级", "中级", "高级"]
    diets = ["均衡", "高蛋白", "低碳水", "低脂", "素食"]
    injuries = ["膝", "腰", "肩", "腕", "踝", "其他"]

    def rand_injury():
        if RNG.random() < 0.6:
            return "无"
        k = RNG.integers(1, 3)
        return ";".join(RNG.choice(injuries, size=k, replace=False))

    return pd.DataFrame(
        {
            "gender": RNG.integers(0, 2, n),
            "age": RNG.integers(18, 61, n),
            "height_cm": RNG.uniform(150, 195, n).round(1),
            "weight_kg": RNG.uniform(45, 110, n).round(1),
            "goal": RNG.choice(goals, n),
            "experience_level": RNG.choice(exps, n),
            "weekly_hours": RNG.uniform(1, 21, n).round(1),
            "diet_preference": RNG.choice(diets, n),
            "injury": [rand_injury() for _ in range(n)],
        }
    )


def make_body_performance(n=13393):
    return pd.DataFrame(
        {
            "age": RNG.uniform(21, 65, n).round(0),
            "gender": RNG.integers(0, 2, n),
            "height_cm": RNG.uniform(125, 194, n).round(1),
            "weight_kg": RNG.uniform(26, 138, n).round(1),
            "body_fat_pct": RNG.uniform(3, 45, n).round(1),
            "diastolic": RNG.uniform(55, 120, n).round(0),
            "systolic": RNG.uniform(90, 180, n).round(0),
            "grip_force": RNG.uniform(10, 70, n).round(1),
            "sit_bend_forward_cm": RNG.uniform(-20, 40, n).round(1),
            "sit_ups_counts": RNG.integers(0, 80, n),
            "broad_jump_cm": RNG.uniform(50, 300, n).round(0),
            "class": RNG.choice(["A", "B", "C", "D"], n),
        }
    )


if __name__ == "__main__":
    survey = make_survey(500)
    survey.to_csv("data/raw/survey.csv", index=False, encoding="utf-8-sig")

    bp = make_body_performance(13393)
    bp.to_csv("data/raw/body_performance.csv", index=False, encoding="utf-8")

    print("survey.csv rows:", len(survey))
    print("body_performance.csv rows:", len(bp))
