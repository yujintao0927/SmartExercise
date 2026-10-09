"""模型训练：SMOTE 平衡 + 随机森林 + 网格搜索 + 评估（T-5/T-6/T-7）。

训练 5 个分类器分别预测 6 类输出中的 5 个结构化标签（动作组合由动作库后处理），
其中 target_goal 用 SMOTE 平衡 + GridSearchCV 调优，其余用默认参数训练。
"""
import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GridSearchCV, train_test_split

PROCESSED = "data/processed"


def main():
    d = joblib.load(f"{PROCESSED}/train.joblib")
    X, y_df, encoders = d["X"], d["y"], d["encoders"]

    # 目标分类列与其余输出列
    target = "target_goal"
    other_cols = ["weekly_frequency", "session_duration_min", "intensity_level", "training_cycle_weeks"]

    # T-5：SMOTE 平衡（针对主分类 target_goal）
    y_goal = y_df[target]
    print("before SMOTE:", y_goal.value_counts().to_dict())
    smote = SMOTE(random_state=42, k_neighbors=5)
    X_res, y_res = smote.fit_resample(X, y_goal)
    print("after SMOTE:", pd.Series(y_res).value_counts().to_dict())

    X_train, X_test, y_train, y_test = train_test_split(
        X_res, y_res, test_size=0.2, random_state=42, stratify=y_res
    )

    # T-6：GridSearchCV 调优主分类模型
    param_grid = {"n_estimators": [50, 100], "max_depth": [10, 20, None]}
    grid = GridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid, cv=3, scoring="f1_weighted", n_jobs=-1,
    )
    grid.fit(X_train, y_train)
    print("best params:", grid.best_params_)
    model = grid.best_estimator_

    # T-7：评估主分类模型
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    print(f"[{target}] accuracy={acc:.4f} weighted_f1={f1:.4f}")

    # 其余输出用默认参数训练（无需 SMOTE）
    models = {target: model}
    metrics = {target: {"accuracy": acc, "f1": f1}}
    for col in other_cols:
        y_col = y_df[col]
        Xtr, Xte, ytr, yte = train_test_split(
            X, y_col, test_size=0.2, random_state=42, stratify=y_col
        )
        clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        clf.fit(Xtr, ytr)
        p = clf.predict(Xte)
        a = accuracy_score(yte, p)
        f = f1_score(yte, p, average="weighted")
        print(f"[{col}] accuracy={a:.4f} weighted_f1={f:.4f}")
        models[col] = clf
        metrics[col] = {"accuracy": a, "f1": f}

    # 特征重要性
    feature_names = ["gender", "age", "height_cm", "weight_kg", "weekly_hours", "bmi",
                     "goal", "experience_level", "diet_preference"]
    injury_names = list(encoders["injury_mlb"].classes_)
    feature_names += [f"injury_{n}" for n in injury_names]
    importance = pd.DataFrame(
        {"feature": feature_names, "importance": model.feature_importances_}
    ).sort_values("importance", ascending=False)
    print(importance.head(15).to_string(index=False))

    # 保存模型与评估结果
    joblib.dump(
        {
            "models": models,
            "encoders": encoders,
            "best_params": grid.best_params_,
            "metrics": metrics,
            "feature_importance": importance,
        },
        f"{PROCESSED}/model.joblib",
    )
    importance.to_csv(f"{PROCESSED}/feature_importance.csv", index=False, encoding="utf-8-sig")
    print("model saved to data/processed/model.joblib")


if __name__ == "__main__":
    main()
