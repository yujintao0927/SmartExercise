"""生成训练集并做特征编码（T-4）。

用规则引擎从 9 特征空间采样生成训练样本，对输入特征编码，
保存编码器与编码后数据到 data/processed/，供 T-5/T-6 使用。
"""
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer, StandardScaler

from ml.feature_dictionary import FEATURES
from ml.rule_engine import recommend

RNG = np.random.default_rng(42)
PROCESSED = "data/processed"

CAT_FEATURES = ["goal", "experience_level", "diet_preference"]
NUM_FEATURES = ["age", "height_cm", "weight_kg", "weekly_hours"]


def sample_features(n):
    goals = FEATURES["goal"]["values"]
    exps = FEATURES["experience_level"]["values"]
    diets = FEATURES["diet_preference"]["values"]
    injuries = FEATURES["injury"]["values"]

    def rand_injury():
        if RNG.random() < 0.6:
            return "无"
        k = RNG.integers(1, 3)
        return ";".join(RNG.choice(injuries[1:], size=k, replace=False))

    return pd.DataFrame(
        {
            "gender": RNG.integers(0, 2, n),
            "age": RNG.integers(14, 71, n),
            "height_cm": RNG.uniform(140, 211, n).round(1),
            "weight_kg": RNG.uniform(35, 201, n).round(1),
            "goal": RNG.choice(goals, n, p=[0.40, 0.25, 0.15, 0.10, 0.10]),
            "experience_level": RNG.choice(exps, n),
            "weekly_hours": RNG.uniform(1, 21, n).round(1),
            "diet_preference": RNG.choice(diets, n),
            "injury": [rand_injury() for _ in range(n)],
        }
    )


def build(n=80000):
    feats = sample_features(n)
    recs = [recommend(**row) for row in feats.to_dict("records")]
    out = pd.DataFrame(recs)
    data = pd.concat([feats, out], axis=1)
    data["bmi"] = (data["weight_kg"] / (data["height_cm"] / 100) ** 2).round(1)
    return data


def encode(data):
    """编码输入特征，返回特征矩阵与编码器。"""
    label_encoders = {}
    for col in CAT_FEATURES:
        le = LabelEncoder()
        data[col + "_enc"] = le.fit_transform(data[col])
        label_encoders[col] = le

    mlb = MultiLabelBinarizer()
    injury_lists = data["injury"].apply(lambda s: [x for x in s.split(";") if x != "无"])
    injury_mat = mlb.fit_transform(injury_lists)

    scaler = StandardScaler()
    num_mat = scaler.fit_transform(data[NUM_FEATURES + ["bmi"]])

    X = np.hstack(
        [
            data[["gender"]].values,
            num_mat,
            data[[c + "_enc" for c in CAT_FEATURES]].values,
            injury_mat,
        ]
    )
    encoders = {"label": label_encoders, "injury_mlb": mlb, "scaler": scaler}
    return X, encoders


if __name__ == "__main__":
    os.makedirs(PROCESSED, exist_ok=True)
    data = build(80000)
    X, encoders = encode(data)

    # 标签（exercise_plan 由动作库后处理，不参与编码）
    y = data[
        ["target_goal", "weekly_frequency", "session_duration_min",
         "intensity_level", "training_cycle_weeks"]
    ]

    data.to_csv(f"{PROCESSED}/train_data.csv", index=False, encoding="utf-8-sig")
    joblib.dump({"X": X, "y": y, "encoders": encoders}, f"{PROCESSED}/train.joblib")
    print("train_data rows:", len(data))
    print("X shape:", X.shape)
    print("y cols:", list(y.columns))
