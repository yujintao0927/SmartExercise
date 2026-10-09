"""训练统计与新增 schema 校验测试。"""
from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.schemas import ExerciseIn, PasswordIn, StatusIn, TemplateIn
from app.services import training_stats


def _db(records):
    db = MagicMock()
    db.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = records
    return db


def _rec(days_ago, completion=1.0):
    r = MagicMock()
    r.train_date = date.today() - timedelta(days=days_ago)
    r.completion_rate = completion
    return r


# ---------- training_stats ----------

def test_streak_consecutive():
    s = training_stats(_db([_rec(0), _rec(1), _rec(2)]), 1)
    assert s["streak_days"] == 3
    assert s["total_sessions"] == 3


def test_streak_broken():
    s = training_stats(_db([_rec(0), _rec(1), _rec(3)]), 1)
    assert s["streak_days"] == 2


def test_empty_stats():
    s = training_stats(_db([]), 1)
    assert s["streak_days"] == 0
    assert s["total_sessions"] == 0
    assert s["week_sessions"] == 0


def test_week_stats():
    s = training_stats(_db([_rec(0, 1.0), _rec(3, 0.5), _rec(10, 1.0)]), 1)
    assert s["week_sessions"] == 2
    assert s["week_completion_avg"] == 0.75


# ---------- 新增 schema 校验 ----------

def test_password_min_length():
    with pytest.raises(ValidationError):
        PasswordIn(old_password="123456", new_password="123")


def test_exercise_requires_name():
    with pytest.raises(ValidationError):
        ExerciseIn(name="", muscle_group="背", exercise_type="力量")


def test_status_requires_bool():
    with pytest.raises(ValidationError):
        StatusIn(active="xyz")


def test_template_frequency_range():
    with pytest.raises(ValidationError):
        TemplateIn(goal="增肌", intensity_level="中", exercise_ids=[1], sets=4,
                   reps=8, session_duration_min=60, weekly_frequency=9,
                   training_cycle_weeks=8)
