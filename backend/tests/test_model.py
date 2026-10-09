"""T-24 模型推理一致性测试。"""
from app import services
from app.schemas import ProfileIn

PROFILE = dict(gender=0, age=25, height_cm=175, weight_kg=70, goal="增肌",
               experience_level="初级", weekly_hours=6, diet_preference="高蛋白", injury=["无"])


def test_predict_consistent():
    p = ProfileIn(**PROFILE)
    assert services.predict_profile(p) == services.predict_profile(p)


def test_predict_returns_six_fields():
    p = ProfileIn(**PROFILE)
    r = services.predict_profile(p)
    assert set(r) == {"target_goal", "weekly_frequency", "session_duration_min",
                      "intensity_level", "training_cycle_weeks"}
