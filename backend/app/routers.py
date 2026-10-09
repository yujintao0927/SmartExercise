"""API 路由（T-10 ~ T-15a）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import services
from .database import get_db
from .models import BodyMetric, RecommendationRecord, TrainingRecord, User, UserProfile
from .schemas import (
    BodyMetricIn, LoginIn, ProfileIn, ProfileOut, RecommendOut,
    RegisterIn, TokenOut, TrainingRecordIn,
)
from .security import (
    create_token, get_current_user, hash_password, require_admin, verify_password,
)

router = APIRouter(prefix="/api")


# T-10 认证
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
    return TokenOut(access_token=create_token(user.id, user.role))


# T-11 画像
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


# T-12 推荐
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


# T-13 训练记录
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


# T-14 仪表盘 + 身体指标
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


# T-15a 管理员（最小）
@router.get("/admin/users")
def admin_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "role": u.role,
             "created_at": str(u.created_at)} for u in users]


@router.get("/admin/model")
def admin_model(_: User = Depends(require_admin)):
    m = services.load_model()
    return {"loaded": True, "best_params": m.get("best_params"), "metrics": m.get("metrics")}
