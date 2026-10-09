"""Pydantic 请求/响应模型（T-9）。"""
from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

Goal = Literal["减脂", "增肌", "塑形", "提升耐力", "保持健康"]
Experience = Literal["新手", "初级", "中级", "高级"]
Diet = Literal["均衡", "高蛋白", "低碳水", "低脂", "素食"]
InjuryPart = Literal["无", "膝", "腰", "肩", "腕", "踝", "其他"]


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileIn(BaseModel):
    gender: int = Field(ge=0, le=1)
    age: int = Field(ge=14, le=70)
    height_cm: float = Field(ge=140, le=210)
    weight_kg: float = Field(ge=35, le=200)
    goal: Goal
    experience_level: Experience
    weekly_hours: float = Field(ge=1, le=21)
    diet_preference: Diet
    injury: List[InjuryPart]

    @field_validator("injury")
    @classmethod
    def injury_exclusive(cls, v):
        if "无" in v and len(v) > 1:
            raise ValueError("「无」不能与其他部位同时选择")
        if len(v) == 0:
            raise ValueError("至少选择一个伤病状态")
        return v


class ProfileOut(BaseModel):
    gender: int
    age: int
    height_cm: float
    weight_kg: float
    goal: str
    experience_level: str
    weekly_hours: float
    diet_preference: str
    injury: List[str]


class TrainingRecordIn(BaseModel):
    train_date: date
    completion_rate: float = Field(ge=0, le=1)
    fatigue_score: int = Field(ge=1, le=10)
    feedback: Optional[Literal["太轻松", "适中", "太累"]] = None
    duration_min: Optional[int] = None


class BodyMetricIn(BaseModel):
    record_date: date
    weight_kg: float = Field(gt=0)


class RecommendOut(BaseModel):
    target_goal: str
    weekly_frequency: int
    exercise_plan: List[dict]
    session_duration_min: int
    intensity_level: str
    training_cycle_weeks: int
    model_version: str
