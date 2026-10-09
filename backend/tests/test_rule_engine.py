"""T-23 规则引擎测试。"""
from ml.rule_engine import recommend


def test_advanced_muscle_gain_high_intensity():
    r = recommend(0, 25, 175, 70, "增肌", "高级", 12, "高蛋白", "无")
    assert r["target_goal"] == "增肌"
    assert r["intensity_level"] == "高"


def test_beginner_low_intensity():
    r = recommend(0, 25, 175, 70, "减脂", "新手", 3, "均衡", "无")
    assert r["intensity_level"] == "低"


def test_injury_lowers_intensity():
    r = recommend(0, 25, 175, 70, "增肌", "中级", 6, "高蛋白", "膝")
    assert r["intensity_level"] == "中"


def test_frequency_by_time():
    r = recommend(0, 25, 175, 70, "减脂", "初级", 12, "均衡", "无")
    assert r["weekly_frequency"] == 5
