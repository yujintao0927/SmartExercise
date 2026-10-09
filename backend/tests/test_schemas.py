"""T-9 Pydantic 校验测试。"""
import pytest
from pydantic import ValidationError

from app.schemas import ProfileIn

BASE = dict(gender=0, age=25, height_cm=175, weight_kg=70, goal="增肌",
            experience_level="初级", weekly_hours=6, diet_preference="高蛋白", injury=["无"])


def test_valid():
    p = ProfileIn(**BASE)
    assert p.goal == "增肌"


def test_injury_exclusive():
    with pytest.raises(ValidationError):
        ProfileIn(**{**BASE, "injury": ["无", "膝"]})


def test_age_range():
    with pytest.raises(ValidationError):
        ProfileIn(**{**BASE, "age": 100})


def test_goal_invalid():
    with pytest.raises(ValidationError):
        ProfileIn(**{**BASE, "goal": "错误"})
