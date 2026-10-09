"""业务逻辑：模型推理 + 动作组合组装 + 动态调整规则（T-12/T-15）。"""
import joblib
import numpy as np
from sqlalchemy.orm import Session

from .models import Exercise, PlanTemplate, TrainingRecord

MODEL_PATH = "data/processed/model.joblib"
_model = None


def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def _encode_profile(gender, age, height_cm, weight_kg, goal, experience_level,
                    weekly_hours, diet_preference, injury):
    """把画像编码为特征向量（与 build_dataset 的 encode 保持一致）。"""
    enc = load_model()["encoders"]
    bmi = weight_kg / (height_cm / 100) ** 2
    num = enc["scaler"].transform([[age, height_cm, weight_kg, weekly_hours, bmi]])
    goal_enc = enc["label"]["goal"].transform([goal])[0]
    exp_enc = enc["label"]["experience_level"].transform([experience_level])[0]
    diet_enc = enc["label"]["diet_preference"].transform([diet_preference])[0]
    injury_vec = enc["injury_mlb"].transform([[x for x in injury if x != "无"]])[0]
    return np.hstack([[[gender]], num, [[goal_enc, exp_enc, diet_enc]], [injury_vec]])


def predict_profile(profile) -> dict:
    """预测 5 个结构化输出标签。"""
    x = _encode_profile(
        profile.gender, profile.age, profile.height_cm, profile.weight_kg,
        profile.goal, profile.experience_level, profile.weekly_hours,
        profile.diet_preference, profile.injury,
    )
    models = load_model()["models"]
    return {
        "target_goal": models["target_goal"].predict(x)[0],
        "weekly_frequency": int(models["weekly_frequency"].predict(x)[0]),
        "session_duration_min": int(models["session_duration_min"].predict(x)[0]),
        "intensity_level": models["intensity_level"].predict(x)[0],
        "training_cycle_weeks": int(models["training_cycle_weeks"].predict(x)[0]),
    }


def get_exercise_plan(db: Session, goal: str, intensity: str) -> list:
    """从 plan_template 查询动作组合。"""
    tpl = db.query(PlanTemplate).filter_by(goal=goal, intensity_level=intensity).first()
    if not tpl:
        return []
    exs = db.query(Exercise).filter(Exercise.id.in_(tpl.exercise_ids)).all()
    return [{"name": e.name, "sets": tpl.sets, "reps": tpl.reps} for e in exs]


def recommend(db: Session, profile, model_version: str) -> dict:
    """完整推荐：5 个输出标签 + 动作组合 + 模型版本。"""
    result = predict_profile(profile)
    result["exercise_plan"] = get_exercise_plan(db, result["target_goal"], result["intensity_level"])
    result["model_version"] = model_version
    return result


def adjust_plan(db: Session, user_id: int) -> dict:
    """动态调整规则（T-15）：综合完成率与疲劳评分给出频率/强度建议。"""
    records = (
        db.query(TrainingRecord)
        .filter_by(user_id=user_id)
        .order_by(TrainingRecord.train_date.desc())
        .limit(10)
        .all()
    )
    if len(records) < 3:
        return {"available": False, "advice": "打卡记录不足，暂不调整"}

    avg_completion = sum(r.completion_rate for r in records) / len(records)
    avg_fatigue = sum(r.fatigue_score for r in records) / len(records)

    if avg_completion < 0.5 or avg_fatigue >= 8:
        return {"available": True, "frequency_delta": -1, "intensity_delta": -1,
                "advice": "完成率偏低或疲劳偏高，建议降低频率与强度"}
    if avg_completion > 0.9 and avg_fatigue <= 4:
        return {"available": True, "frequency_delta": 1, "intensity_delta": 1,
                "advice": "完成率高且疲劳低，建议提升频率与强度"}
    return {"available": True, "frequency_delta": 0, "intensity_delta": 0,
            "advice": "维持当前计划"}
