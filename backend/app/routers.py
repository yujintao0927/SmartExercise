"""API 路由（T-10 ~ T-15a + 用户/管理员扩展）。"""
import secrets
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from . import services
from .database import get_db
from .models import (
    BodyMetric, Exercise, PlanTemplate, RecommendationRecord,
    TrainingRecord, User, UserProfile,
)
from .schemas import (
    BodyMetricIn, ExerciseIn, LoginIn, PasswordIn, ProfileIn, ProfileOut,
    RecommendOut, RegisterIn, ResetPwdIn, StatusIn, TemplateIn, TokenOut,
    TrainingRecordIn,
)
from .security import (
    create_token, get_current_user, hash_password, require_admin, verify_password,
)

router = APIRouter(prefix="/api")


def _user_dict(u: User) -> dict:
    return {"id": u.id, "username": u.username, "role": u.role,
            "active": u.active, "created_at": str(u.created_at)}


# ==================== 认证 ====================

@router.post("/auth/register", status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=body.username).first():
        raise HTTPException(status_code=409, detail="用户名已存在")
    user = User(username=body.username, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username}


@router.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    return TokenOut(access_token=create_token(user.id, user.role))


@router.get("/auth/me")
def get_me(user: User = Depends(get_current_user)):
    return _user_dict(user)


@router.put("/auth/password")
def change_password(body: PasswordIn, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    if not verify_password(body.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码错误")
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return {"message": "密码已更新"}


# ==================== 画像 ====================

@router.put("/profile", response_model=ProfileOut)
def upsert_profile(body: ProfileIn, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    profile = db.query(UserProfile).filter_by(user_id=user.id).first()
    if profile:
        for k, v in body.model_dump().items():
            setattr(profile, k, v)
    else:
        profile = UserProfile(user_id=user.id, **body.model_dump())
        db.add(profile)
    db.commit()
    db.refresh(profile)
    return ProfileOut(**{k: getattr(profile, k) for k in ProfileOut.model_fields})


@router.get("/profile", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = db.query(UserProfile).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="画像未录入")
    return ProfileOut(**{k: getattr(profile, k) for k in ProfileOut.model_fields})


# ==================== 推荐 ====================

@router.post("/recommend", response_model=RecommendOut)
def make_recommend(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = db.query(UserProfile).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="请先录入画像")
    result = services.recommend(db, profile, model_version="rf-v1.0")
    db.add(RecommendationRecord(user_id=user.id, **result))
    db.commit()
    return result


@router.get("/recommend/history")
def recommend_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(RecommendationRecord)
        .filter_by(user_id=user.id)
        .order_by(RecommendationRecord.created_at.desc())
        .all()
    )


# ==================== 训练 ====================

@router.post("/training/records", status_code=201)
def add_training(body: TrainingRecordIn, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    rec = TrainingRecord(user_id=user.id, **body.model_dump())
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {"id": rec.id}


@router.get("/training/records")
def list_training(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(TrainingRecord)
        .filter_by(user_id=user.id)
        .order_by(TrainingRecord.train_date.desc())
        .all()
    )


@router.get("/training/stats")
def training_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return services.training_stats(db, user.id)


# ==================== 身体指标 / 仪表盘 ====================

@router.post("/metrics/weight", status_code=201)
def add_weight(body: BodyMetricIn, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    profile = db.query(UserProfile).filter_by(user_id=user.id).first()
    height = profile.height_cm if profile else None
    bmi = round(body.weight_kg / (height / 100) ** 2, 1) if height else None
    rec = BodyMetric(user_id=user.id, record_date=body.record_date,
                     weight_kg=body.weight_kg, bmi=bmi)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {"id": rec.id, "bmi": bmi}


@router.get("/metrics/weight")
def list_weight(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(BodyMetric)
        .filter_by(user_id=user.id)
        .order_by(BodyMetric.record_date.desc())
        .all()
    )


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    training = (
        db.query(TrainingRecord)
        .filter_by(user_id=user.id)
        .order_by(TrainingRecord.train_date.asc())
        .all()
    )
    weight = (
        db.query(BodyMetric)
        .filter_by(user_id=user.id)
        .order_by(BodyMetric.record_date.asc())
        .all()
    )
    return {
        "training": [{"date": str(t.train_date), "completion_rate": t.completion_rate,
                      "fatigue_score": t.fatigue_score} for t in training],
        "weight": [{"date": str(w.record_date), "weight_kg": w.weight_kg} for w in weight],
        "adjustment": services.adjust_plan(db, user.id),
    }


# ==================== 管理员：总览 ====================

@router.get("/admin/overview")
def admin_overview(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    today = datetime.utcnow().date()
    week_ago = date.today() - timedelta(days=7)

    total_users = db.query(User).count()
    new_today = db.query(User).filter(User.created_at >= today).count()
    total_recs = db.query(RecommendationRecord).count()
    total_sessions = db.query(TrainingRecord).count()
    active_week = (
        db.query(func.count(func.distinct(TrainingRecord.user_id)))
        .filter(TrainingRecord.train_date >= week_ago)
        .scalar()
    )

    growth = []
    for i in range(9, -1, -1):
        d = date.today() - timedelta(days=i)
        start = datetime(d.year, d.month, d.day)
        end = start + timedelta(days=1)
        cnt = db.query(User).filter(User.created_at >= start, User.created_at < end).count()
        growth.append({"date": d.strftime("%m-%d"), "count": cnt})

    goal_rows = db.query(UserProfile.goal, func.count()).group_by(UserProfile.goal).all()
    goal_dist = [{"goal": g, "count": c} for g, c in goal_rows]

    buckets = [("80-100%", 0.8, 1.01), ("60-80%", 0.6, 0.8),
               ("40-60%", 0.4, 0.6), ("0-40%", 0.0, 0.4)]
    rates = [r for (r,) in db.query(TrainingRecord.completion_rate).all()]
    completion = [
        {"range": label, "count": sum(1 for r in rates if lo <= r < hi)}
        for label, lo, hi in buckets
    ]

    return {
        "kpi": {
            "total_users": total_users,
            "new_users_today": new_today,
            "total_recommendations": total_recs,
            "total_sessions": total_sessions,
            "active_users_week": active_week or 0,
        },
        "user_growth": growth,
        "goal_distribution": goal_dist,
        "completion_distribution": completion,
    }


# ==================== 管理员：用户 ====================

@router.get("/admin/users")
def admin_users(search: str = "", role: str = "", db: Session = Depends(get_db),
                _: User = Depends(require_admin)):
    q = db.query(User)
    if search:
        q = q.filter(User.username.contains(search))
    if role:
        q = q.filter(User.role == role)
    users = q.order_by(User.id.asc()).all()
    return {"items": [_user_dict(u) for u in users], "total": len(users)}


@router.get("/admin/users/{user_id}")
def admin_user_detail(user_id: int, db: Session = Depends(get_db),
                      _: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    profile = db.query(UserProfile).filter_by(user_id=user_id).first()
    recent_training = (
        db.query(TrainingRecord).filter_by(user_id=user_id)
        .order_by(TrainingRecord.train_date.desc()).limit(3).all()
    )
    recent_recs = (
        db.query(RecommendationRecord).filter_by(user_id=user_id)
        .order_by(RecommendationRecord.created_at.desc()).limit(2).all()
    )
    return {
        **_user_dict(user),
        "profile": {
            "age": profile.age, "goal": profile.goal,
            "height_cm": profile.height_cm, "weight_kg": profile.weight_kg,
        } if profile else None,
        "recent_training": [{"train_date": str(t.train_date),
                             "completion_rate": t.completion_rate} for t in recent_training],
        "recent_recommendations": [{"target_goal": r.target_goal,
                                    "created_at": str(r.created_at)} for r in recent_recs],
    }


@router.patch("/admin/users/{user_id}/status")
def set_user_status(user_id: int, body: StatusIn, db: Session = Depends(get_db),
                    _: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.active = body.active
    db.commit()
    return {"id": user.id, "active": user.active}


@router.delete("/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db),
                _: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="不能删除管理员")
    for model in (UserProfile, TrainingRecord, BodyMetric, RecommendationRecord):
        db.query(model).filter_by(user_id=user_id).delete()
    db.delete(user)
    db.commit()
    return {"message": "已删除"}


@router.post("/admin/users/{user_id}/reset-password")
def reset_password(user_id: int, body: ResetPwdIn | None = None,
                   db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    new_pwd = (body.new_password if body and body.new_password else secrets.token_hex(4))
    user.password_hash = hash_password(new_pwd)
    db.commit()
    return {"username": user.username, "new_password": new_pwd}


# ==================== 管理员：推荐 / 训练 ====================

@router.get("/admin/recommendations")
def admin_recommendations(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = (
        db.query(RecommendationRecord, User.username)
        .join(User, RecommendationRecord.user_id == User.id)
        .order_by(RecommendationRecord.created_at.desc())
        .all()
    )
    items = [{
        "id": r.id, "user_id": r.user_id, "username": username,
        "target_goal": r.target_goal, "intensity_level": r.intensity_level,
        "created_at": str(r.created_at),
    } for r, username in rows]
    return {"items": items, "total": len(items)}


@router.get("/admin/training")
def admin_training(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = db.query(TrainingRecord.completion_rate, TrainingRecord.fatigue_score).all()
    total = len(rows)
    avg_comp = round(sum(r[0] for r in rows) / total, 4) if total else 0.0
    avg_fatigue = round(sum(r[1] for r in rows) / total, 2) if total else 0.0
    buckets = [("80-100%", 0.8, 1.01), ("60-80%", 0.6, 0.8),
               ("40-60%", 0.4, 0.6), ("0-40%", 0.0, 0.4)]
    completion = [
        {"range": label, "count": sum(1 for r in rows if lo <= r[0] < hi)}
        for label, lo, hi in buckets
    ]
    return {
        "total_sessions": total,
        "avg_completion": avg_comp,
        "avg_fatigue": avg_fatigue,
        "completion_distribution": completion,
    }


# ==================== 管理员：动作库 ====================

@router.get("/admin/exercises")
def admin_exercises(muscle_group: str = "", exercise_type: str = "",
                    db: Session = Depends(get_db), _: User = Depends(require_admin)):
    q = db.query(Exercise)
    if muscle_group:
        q = q.filter(Exercise.muscle_group == muscle_group)
    if exercise_type:
        q = q.filter(Exercise.exercise_type == exercise_type)
    return q.order_by(Exercise.id.asc()).all()


@router.post("/admin/exercises", status_code=201)
def create_exercise(body: ExerciseIn, db: Session = Depends(get_db),
                    _: User = Depends(require_admin)):
    ex = Exercise(**body.model_dump())
    db.add(ex)
    db.commit()
    db.refresh(ex)
    return ex


@router.put("/admin/exercises/{exercise_id}")
def update_exercise(exercise_id: int, body: ExerciseIn, db: Session = Depends(get_db),
                    _: User = Depends(require_admin)):
    ex = db.get(Exercise, exercise_id)
    if not ex:
        raise HTTPException(status_code=404, detail="动作不存在")
    for k, v in body.model_dump().items():
        setattr(ex, k, v)
    db.commit()
    db.refresh(ex)
    return ex


@router.delete("/admin/exercises/{exercise_id}")
def delete_exercise(exercise_id: int, db: Session = Depends(get_db),
                    _: User = Depends(require_admin)):
    ex = db.get(Exercise, exercise_id)
    if not ex:
        raise HTTPException(status_code=404, detail="动作不存在")
    db.delete(ex)
    db.commit()
    return {"message": "已删除"}


# ==================== 管理员：计划模板 ====================

@router.get("/admin/templates")
def admin_templates(goal: str = "", intensity_level: str = "",
                    db: Session = Depends(get_db), _: User = Depends(require_admin)):
    q = db.query(PlanTemplate)
    if goal:
        q = q.filter(PlanTemplate.goal == goal)
    if intensity_level:
        q = q.filter(PlanTemplate.intensity_level == intensity_level)
    return q.order_by(PlanTemplate.id.asc()).all()


@router.post("/admin/templates", status_code=201)
def create_template(body: TemplateIn, db: Session = Depends(get_db),
                    _: User = Depends(require_admin)):
    tpl = PlanTemplate(**body.model_dump())
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return tpl


@router.put("/admin/templates/{template_id}")
def update_template(template_id: int, body: TemplateIn, db: Session = Depends(get_db),
                    _: User = Depends(require_admin)):
    tpl = db.get(PlanTemplate, template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    for k, v in body.model_dump().items():
        setattr(tpl, k, v)
    db.commit()
    db.refresh(tpl)
    return tpl


@router.delete("/admin/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db),
                    _: User = Depends(require_admin)):
    tpl = db.get(PlanTemplate, template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    db.delete(tpl)
    db.commit()
    return {"message": "已删除"}


# ==================== 管理员：模型 ====================

@router.get("/admin/model")
def admin_model(_: User = Depends(require_admin)):
    m = services.load_model()
    return {"loaded": True, "best_params": m.get("best_params"), "metrics": m.get("metrics")}
