"""SQLAlchemy ORM 模型（7 张表，对应 design.md §2.2）。"""
from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    role = Column(String(20), default="user")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, nullable=False)
    gender = Column(Integer, nullable=False)          # 0=男 1=女
    age = Column(Integer, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    goal = Column(String(20), nullable=False)
    experience_level = Column(String(20), nullable=False)
    weekly_hours = Column(Float, nullable=False)
    diet_preference = Column(String(20), nullable=False)
    injury = Column(JSON, nullable=False, default=list)  # 多选部位数组，如 ["膝","腰"]；无伤病 ["无"]
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RecommendationRecord(Base):
    __tablename__ = "recommendation_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    target_goal = Column(String(20))
    weekly_frequency = Column(Integer)
    exercise_plan = Column(JSON)          # [{name, sets, reps}]
    session_duration_min = Column(Integer)
    intensity_level = Column(String(10))
    training_cycle_weeks = Column(Integer)
    model_version = Column(String(30))
    created_at = Column(DateTime, default=datetime.utcnow)


class TrainingRecord(Base):
    __tablename__ = "training_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    train_date = Column(Date, nullable=False)
    completion_rate = Column(Float)        # 0-1
    fatigue_score = Column(Integer)        # 1-10
    feedback = Column(String(20))          # 太轻松/适中/太累
    duration_min = Column(Integer)


class BodyMetric(Base):
    __tablename__ = "body_metric"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    record_date = Column(Date, nullable=False)
    weight_kg = Column(Float)
    bmi = Column(Float)


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    muscle_group = Column(String(30))
    exercise_type = Column(String(20))     # 力量/有氧/柔韧


class PlanTemplate(Base):
    __tablename__ = "plan_template"

    id = Column(Integer, primary_key=True, autoincrement=True)
    goal = Column(String(20), nullable=False)
    intensity_level = Column(String(10), nullable=False)
    exercise_ids = Column(JSON, default=list)  # 引用 exercise 的 id 数组
    sets = Column(Integer)
    reps = Column(Integer)
    session_duration_min = Column(Integer)
    weekly_frequency = Column(Integer)
    training_cycle_weeks = Column(Integer)
