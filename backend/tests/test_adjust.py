"""T-23 动态调整规则测试（mock DB）。"""
from unittest.mock import MagicMock

from app.services import adjust_plan


def _db(records):
    db = MagicMock()
    db.query.return_value.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = records
    return db


def test_low_completion_lowers():
    rs = [MagicMock(completion_rate=0.3, fatigue_score=5) for _ in range(4)]
    r = adjust_plan(_db(rs), 1)
    assert r["frequency_delta"] == -1


def test_high_completion_raises():
    rs = [MagicMock(completion_rate=0.95, fatigue_score=3) for _ in range(4)]
    r = adjust_plan(_db(rs), 1)
    assert r["frequency_delta"] == 1


def test_insufficient_records():
    rs = [MagicMock(completion_rate=0.5, fatigue_score=5) for _ in range(2)]
    r = adjust_plan(_db(rs), 1)
    assert r["available"] is False
