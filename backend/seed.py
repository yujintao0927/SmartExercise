"""初始化动作字典与计划模板种子数据（T-8a）。

把规则引擎的动作库迁移到 exercise（动作字典）与 plan_template（计划模板）表，
供推荐接口组装动作组合时查询。
"""
from sqlalchemy import inspect, text

from app.database import Base, SessionLocal, engine
from app.models import Exercise, PlanTemplate, User
from app.security import hash_password
from ml.rule_engine import EXERCISES

# 动作类型（简单启发式）：有氧/柔韧，其余按力量处理
_CARDIO = {
    "快走", "椭圆机", "慢跑", "动感单车", "HIIT", "跳绳", "划船机", "登山跑",
    "骑行", "游泳", "长跑", "间歇跑", "骑行爬坡", "划船", "散步", "全身循环",
}
_FLEX = {"瑜伽", "普拉提", "拉伸", "太极"}


def classify(name):
    if name in _CARDIO:
        return "全身", "有氧"
    if name in _FLEX:
        return "全身", "柔韧"
    return "全身", "力量"


def seed():
    Base.metadata.create_all(bind=engine)

    # 轻量迁移：为旧库的 user 表补充 active 列（幂等，不删数据）
    insp = inspect(engine)
    if "user" in insp.get_table_names():
        cols = [c["name"] for c in insp.get_columns("user")]
        if "active" not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE user ADD COLUMN active BOOLEAN DEFAULT 1"))

    db = SessionLocal()

    # 默认管理员账号（首次初始化创建，密码 admin123）
    if not db.query(User).filter_by(username="admin").first():
        db.add(User(username="admin", password_hash=hash_password("admin123"), role="admin"))

    # 动作库与模板（幂等：已存在则跳过）
    if db.query(Exercise).first():
        db.commit()
        db.close()
        print("动作库与模板已存在，跳过动作/模板 seed")
        return

    # 收集去重后的动作名
    names = set()
    for exercises in EXERCISES.values():
        names.update(exercises)

    name_to_id = {}
    for name in names:
        muscle, etype = classify(name)
        ex = Exercise(name=name, muscle_group=muscle, exercise_type=etype)
        db.add(ex)
        db.flush()  # 立即拿到自增 id
        name_to_id[name] = ex.id

    for (goal, intensity), exercises in EXERCISES.items():
        db.add(PlanTemplate(
            goal=goal,
            intensity_level=intensity,
            exercise_ids=[name_to_id[n] for n in exercises],
            sets=3,
            reps=12,
            session_duration_min=60,
            weekly_frequency=4,
            training_cycle_weeks=8,
        ))

    db.commit()
    db.close()
    print(f"seeded {len(names)} exercises, {len(EXERCISES)} plan templates")


if __name__ == "__main__":
    seed()
