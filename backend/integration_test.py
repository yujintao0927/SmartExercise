"""端到端集成测试：启动后端后运行，覆盖全部接口（含错误场景）。"""
import json
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000/api"
passed = 0
failed = 0


def req(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(r) as resp:
            status, raw = resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read().decode("utf-8")
    try:
        return status, json.loads(raw) if raw else None
    except json.JSONDecodeError:
        return status, raw


def check(name, cond, extra=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {extra}")


print("== 集成测试开始 ==")
uname = "it_" + str(int(time.time()))

# ---------- 认证 ----------
s, r = req("POST", "/auth/register", {"username": uname, "password": "123456"})
check("注册新用户 201", s == 201, f"s={s} {r}")
s, r = req("POST", "/auth/register", {"username": uname, "password": "123456"})
check("重复注册 409", s == 409, f"s={s}")
s, r = req("POST", "/auth/login", {"username": uname, "password": "123456"})
check("登录 200", s == 200, f"s={s} {r}")
utoken = r.get("access_token") if s == 200 else ""
s, r = req("POST", "/auth/login", {"username": uname, "password": "wrong"})
check("错误密码 401", s == 401, f"s={s}")

s, r = req("POST", "/auth/login", {"username": "admin", "password": "admin123"})
check("管理员登录 200", s == 200, f"s={s} {r}")
atoken = r.get("access_token") if s == 200 else ""

# ---------- auth/me / password ----------
s, r = req("GET", "/auth/me", token=utoken)
check("用户 /auth/me 返回 role=user", s == 200 and r.get("role") == "user", f"s={s} {r}")
s, r = req("GET", "/auth/me", token=atoken)
check("管理员 /auth/me 返回 role=admin", s == 200 and r.get("role") == "admin", f"s={s} {r}")

s, r = req("PUT", "/auth/password", {"old_password": "123456", "new_password": "654321"}, utoken)
check("修改密码 200", s == 200, f"s={s} {r}")
s, r = req("PUT", "/auth/password", {"old_password": "wrong", "new_password": "abcdef"}, utoken)
check("旧密码错误 400", s == 400, f"s={s}")
s, r = req("POST", "/auth/login", {"username": uname, "password": "654321"})
check("新密码登录成功", s == 200, f"s={s}")
# 改回原密码
req("PUT", "/auth/password", {"old_password": "654321", "new_password": "123456"}, utoken)

# ---------- 画像 / 推荐 ----------
s, r = req("PUT", "/profile", {"gender": 0, "age": 25, "height_cm": 175, "weight_kg": 70,
                                "goal": "增肌", "experience_level": "初级", "weekly_hours": 6,
                                "diet_preference": "高蛋白", "injury": ["无"]}, utoken)
check("录入画像 200", s == 200, f"s={s} {r}")
s, r = req("GET", "/profile", token=utoken)
check("获取画像 200", s == 200 and r.get("goal") == "增肌", f"s={s} {r}")

s, r = req("POST", "/recommend", {}, utoken)
check("生成推荐 200", s == 200 and "exercise_plan" in r, f"s={s}")
s, r = req("GET", "/recommend/history", token=utoken)
check("推荐历史 200", s == 200 and len(r) >= 1, f"s={s}")

# ---------- 训练 ----------
s, r = req("POST", "/training/records", {"train_date": "2026-10-09", "completion_rate": 0.9,
                                         "fatigue_score": 5, "feedback": "适中", "duration_min": 60}, utoken)
check("打卡 201", s == 201, f"s={s} {r}")
s, r = req("GET", "/training/records", token=utoken)
check("打卡历史 200", s == 200 and len(r) >= 1, f"s={s}")
s, r = req("GET", "/training/stats", token=utoken)
check("训练统计 200", s == 200 and "streak_days" in r and "total_sessions" in r, f"s={s} {r}")

# ---------- 体重 / 仪表盘 ----------
s, r = req("POST", "/metrics/weight", {"record_date": "2026-10-09", "weight_kg": 68.5}, utoken)
check("记录体重 201", s == 201, f"s={s} {r}")
s, r = req("GET", "/metrics/weight", token=utoken)
check("体重历史 200", s == 200 and len(r) >= 1, f"s={s}")
s, r = req("GET", "/dashboard/summary", token=utoken)
check("仪表盘 200", s == 200 and "adjustment" in r, f"s={s}")

# ---------- 权限 ----------
s, r = req("GET", "/admin/overview", token=utoken)
check("普通用户访问管理接口 403", s == 403, f"s={s}")

# ---------- 管理员 ----------
s, r = req("GET", "/admin/overview", token=atoken)
check("数据总览 200", s == 200 and "kpi" in r and "user_growth" in r, f"s={s}")
s, r = req("GET", "/admin/users", token=atoken)
check("用户列表 200 (items)", s == 200 and "items" in r and "total" in r, f"s={s}")

s, r = req("GET", "/admin/users", token=atoken)
uid = None
for u in r.get("items", []):
    if u["username"] == uname:
        uid = u["id"]
check("能检索到新用户", uid is not None, f"uid={uid}")

s, r = req("GET", f"/admin/users/{uid}", token=atoken)
check("用户详情 200", s == 200 and r.get("profile") is not None, f"s={s} {r}")

s, r = req("PATCH", f"/admin/users/{uid}/status", {"active": False}, token=atoken)
check("禁用用户 200", s == 200 and r.get("active") is False, f"s={s} {r}")
s, r = req("POST", "/auth/login", {"username": uname, "password": "123456"})
check("禁用后登录 403", s == 403, f"s={s}")
s, r = req("PATCH", f"/admin/users/{uid}/status", {"active": True}, token=atoken)
check("重新启用用户 200", s == 200 and r.get("active") is True, f"s={s}")

s, r = req("POST", f"/admin/users/{uid}/reset-password", {}, token=atoken)
check("重置密码 200", s == 200 and "new_password" in r, f"s={s} {r}")

s, r = req("GET", "/admin/recommendations", token=atoken)
check("推荐记录列表 200", s == 200 and "items" in r, f"s={s}")
s, r = req("GET", "/admin/training", token=atoken)
check("训练统计 200", s == 200 and "total_sessions" in r, f"s={s}")

# ---------- 动作库 CRUD ----------
s, r = req("POST", "/admin/exercises", {"name": "测试动作", "muscle_group": "背", "exercise_type": "力量"}, atoken)
check("新增动作 201", s == 201, f"s={s} {r}")
eid = r.get("id") if s == 201 else None
s, r = req("GET", "/admin/exercises", token=atoken)
check("动作列表 200", s == 200 and len(r) >= 1, f"s={s}")
s, r = req("PUT", f"/admin/exercises/{eid}", {"name": "测试动作改", "muscle_group": "胸", "exercise_type": "力量"}, atoken)
check("编辑动作 200", s == 200 and r.get("name") == "测试动作改", f"s={s} {r}")
s, r = req("DELETE", f"/admin/exercises/{eid}", token=atoken)
check("删除动作 200", s == 200, f"s={s} {r}")

# ---------- 模板 CRUD ----------
s, r = req("POST", "/admin/templates", {"goal": "增肌", "intensity_level": "中", "exercise_ids": [1, 2, 3],
                                         "sets": 4, "reps": 8, "session_duration_min": 60,
                                         "weekly_frequency": 4, "training_cycle_weeks": 8}, atoken)
check("新增模板 201", s == 201, f"s={s} {r}")
tid = r.get("id") if s == 201 else None
s, r = req("GET", "/admin/templates", token=atoken)
check("模板列表 200", s == 200 and len(r) >= 1, f"s={s}")
s, r = req("PUT", f"/admin/templates/{tid}", {"goal": "减脂", "intensity_level": "低", "exercise_ids": [10, 11],
                                              "sets": 3, "reps": 12, "session_duration_min": 40,
                                              "weekly_frequency": 3, "training_cycle_weeks": 6}, atoken)
check("编辑模板 200", s == 200 and r.get("goal") == "减脂", f"s={s} {r}")
s, r = req("DELETE", f"/admin/templates/{tid}", token=atoken)
check("删除模板 200", s == 200, f"s={s} {r}")

# ---------- 模型 ----------
s, r = req("GET", "/admin/model", token=atoken)
check("模型信息 200", s == 200 and r.get("loaded") is True, f"s={s}")

# ---------- 删除保护 / 清理 ----------
s, r = req("GET", "/admin/users", token=atoken)
admin_id = next((u["id"] for u in r["items"] if u["username"] == "admin"), None)
s, r = req("DELETE", f"/admin/users/{admin_id}", token=atoken)
check("删除管理员 400", s == 400, f"s={s} {r}")

s, r = req("DELETE", f"/admin/users/{uid}", token=atoken)
check("删除测试用户 200", s == 200, f"s={s} {r}")

print(f"== 集成测试结束：{passed} 通过 / {failed} 失败 ==")
exit(1 if failed else 0)
