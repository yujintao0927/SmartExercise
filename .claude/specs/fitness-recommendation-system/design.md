# 基于机器学习的健身计划推荐系统 — 设计文档

> 版本：v1.0
> 关联需求：requirements.md

---

## 1. 架构概述

采用前后端分离的三层架构：Vue 3 单页应用 → FastAPI REST 服务 → MySQL 持久化 + 离线训练的随机森林模型。

```
┌──────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3 SPA)                       │
│  登录/注册 │ 画像录入 │ 计划推荐 │ 训练打卡 │ 仪表盘(ECharts)  │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP/JSON (Axios, JWT 鉴权)
┌───────────────────────────▼──────────────────────────────────┐
│                      后端 (FastAPI)                            │
│  Auth路由 │ Profile路由 │ Recommend路由 │ Training路由 │ 仪表盘 │
│  Pydantic 校验 │ CORS 中间件 │ JWT 依赖                       │
│              ┌─────────────┴──────────────┐                   │
│              │  Service 层（业务逻辑）      │                   │
│              └─────────────┬──────────────┘                   │
│         ┌──────────────────┼───────────────────┐              │
│         │ SQLAlchemy ORM   │  ML 推理模块        │              │
└─────────┼──────────────────┼───────────────────┘              │
          │                  │ (加载 joblib 模型 + 预处理pipeline) │
┌─────────▼──────────┐  ┌────▼─────────────────────┐            │
│      MySQL          │  │  离线训练产物(模型文件)     │            │
│ user/profile/reco/  │  │  model.joblib / encoder  │            │
│ training/metric     │  └──────────────────────────┘            │
└─────────────────────┘                                          │
```

**技术选型**

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite + Pinia + Vue Router + Axios + ECharts |
| 后端 | Python 3.8+ + FastAPI + SQLAlchemy 2.x + Pydantic v2 + PyJWT |
| 数据库 | MySQL 8.x |
| ML | scikit-learn（RandomForestClassifier）+ imbalanced-learn（SMOTE）+ pandas + joblib |
| 部署 | 本地 Windows 11 + uvicorn 开发服务器 |

---

## 2. 数据模型

### 2.1 ER 关系

```
user 1 ─── 1 user_profile
user 1 ─── N recommendation_record
user 1 ─── N training_record
user 1 ─── N body_metric

plan_template ──(exercise_ids JSON)──> exercise   # 独立字典，不关联 user
```

### 2.2 表定义

#### user（用户）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, auto | 用户 ID |
| username | VARCHAR(50) | unique, not null | 用户名 |
| password_hash | VARCHAR(100) | not null | bcrypt 哈希 |
| role | VARCHAR(20) | default 'user' | 角色（预留） |
| created_at | DATETIME | default now | 注册时间 |

#### user_profile（用户画像）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, auto | 画像 ID |
| user_id | INT | FK→user, unique | 归属用户 |
| gender | TINYINT | not null | 0/1 |
| age | TINYINT | not null | 年龄 |
| height_cm | FLOAT | not null | 身高 |
| weight_kg | FLOAT | not null | 体重 |
| goal | VARCHAR(20) | not null | 运动目标 |
| experience_level | VARCHAR(20) | not null | 运动基础 |
| weekly_hours | FLOAT | not null | 每周可用时间 |
| diet_preference | VARCHAR(20) | not null | 饮食偏好 |
| injury | JSON | not null | 运动伤病（多选部位数组，如 ["膝","腰"]；无伤病存 ["无"]） |
| updated_at | DATETIME | on update | 更新时间 |

> BMI 不单独存储，由 `weight_kg/(height_cm/100)^2` 计算。

#### recommendation_record（推荐记录）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, auto | 记录 ID |
| user_id | INT | FK→user | 用户 |
| target_goal | VARCHAR(20) | | 训练目标 |
| weekly_frequency | TINYINT | | 每周频率 |
| exercise_plan | JSON | | 动作组合 |
| session_duration_min | TINYINT | | 单次时长 |
| intensity_level | VARCHAR(10) | | 强度 |
| training_cycle_weeks | TINYINT | | 周期 |
| model_version | VARCHAR(30) | | 模型版本 |
| created_at | DATETIME | default now | 生成时间 |

#### training_record（训练记录）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, auto | 记录 ID |
| user_id | INT | FK→user | 用户 |
| train_date | DATE | not null | 训练日期 |
| completion_rate | FLOAT | 0–1 | 完成率 |
| fatigue_score | TINYINT | 1–10 | 疲劳评分 |
| feedback | VARCHAR(20) | | 反馈枚举 |
| duration_min | TINYINT | | 实际时长 |

#### body_metric（身体指标）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, auto | 记录 ID |
| user_id | INT | FK→user | 用户 |
| record_date | DATE | not null | 记录日期 |
| weight_kg | FLOAT | | 体重 |
| bmi | FLOAT | | 派生 BMI |

#### exercise（动作字典）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, auto | 动作 ID |
| name | VARCHAR(50) | not null | 动作名称 |
| muscle_group | VARCHAR(30) | | 目标肌群 |
| exercise_type | VARCHAR(20) | | 力量/有氧/柔韧 |

#### plan_template（计划模板）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, auto | 模板 ID |
| goal | VARCHAR(20) | not null | 适用训练目标 |
| intensity_level | VARCHAR(10) | not null | 适用强度 |
| exercise_ids | JSON | | 动作 ID 数组（引用 exercise） |
| sets | TINYINT | | 组数 |
| reps | TINYINT | | 次数 |
| session_duration_min | TINYINT | | 单次时长 |
| weekly_frequency | TINYINT | | 每周频率 |
| training_cycle_weeks | TINYINT | | 周期 |

---

## 3. API 设计

统一前缀 `/api`；除注册/登录外均需 `Authorization: Bearer <JWT>`。

### 3.1 认证

**POST `/api/auth/register`**

```json
// 请求
{ "username": "zou", "password": "123456" }
// 201
{ "id": 1, "username": "zou" }
// 409 用户名已存在
```

**POST `/api/auth/login`**

```json
// 请求
{ "username": "zou", "password": "123456" }
// 200
{ "access_token": "<jwt>", "token_type": "bearer" }
// 401 凭证错误
```

### 3.2 画像

**PUT `/api/profile`** — 录入/更新画像（9 特征，Pydantic 校验）

**GET `/api/profile`** — 返回当前用户画像（不含敏感字段）

### 3.3 推荐

**POST `/api/recommend`** — 生成推荐

```json
// 200
{
  "target_goal": "增肌",
  "weekly_frequency": 4,
  "exercise_plan": [ { "name": "卧推", "sets": 4, "reps": 10 } ],
  "session_duration_min": 60,
  "intensity_level": "中",
  "training_cycle_weeks": 8,
  "model_version": "rf-v1.0"
}
```

**GET `/api/recommend/history`** — 历史推荐列表

### 3.4 训练记录

**POST `/api/training/records`** — 打卡（completion_rate、fatigue_score、feedback、duration_min）

**GET `/api/training/records`** — 历史记录（倒序）

### 3.5 仪表盘

**GET `/api/dashboard/summary`** — 返回完成率趋势、体重趋势序列

**POST `/api/metrics/weight`** — 记录一次体重

### 3.6 管理员（最小）

**GET `/api/admin/users`** — 用户列表（需 `role=admin`）

**GET `/api/admin/model`** — 当前模型版本与加载状态（需 `role=admin`）

---

## 4. 推荐流程时序

```
用户        前端        FastAPI        ML推理模块      MySQL
 │           │            │               │            │
 │─点击推荐─> │            │               │            │
 │           │─POST /api/recommend──────> │            │
 │           │            │─读取画像───────│──────────> │
 │           │            │<──画像数据─────│<───────────│
 │           │            │─特征预处理+推理> │            │
 │           │            │<──6类结果───────│            │
 │           │            │─保存推荐记录────│──────────> │
 │           │<─200 推荐──│               │            │
 │<─展示计划─│            │               │            │
```

---

## 5. ML 模型流水线

### 5.1 离线训练阶段

```
数据加载 ──> 数据清洗 ──> 特征工程 ──> 编码 ──> SMOTE ──> 训练RF ──> GridSearchCV ──> 评估 ──> 保存模型
   │            │            │          │         │          │            │            │
 Kaggle×3    去重/异常     BMI派生    OneHot/   类别平衡    n_estimators  加权F1       model.joblib
 +问卷        缺失填充    目标编码    LabelEnc                max_depth   特征重要性    encoder.pkl
```

- 主数据集：MealPlan and ExerciseSchedule（80,000 条标签样本）
- 补充数据集：Gym Members Exercise Dataset（973）、Body Performance Dataset（13,393）
- 问卷数据：问卷星导出 CSV，本土化样本，统一到 9 特征字典
- 统一特征矩阵维度，特征映射而非直接样本拼接

### 5.2 在线推理阶段

1. 加载 `model.joblib` + 编码器（启动时加载，常驻内存）。
2. 画像 → 预处理（与训练一致）→ 模型 `predict`。
3. 动作组合（exercise_plan）由「训练目标 + 强度」查询 plan_template 模板表（关联 exercise 动作字典）得到，模型负责其余分类标签。

### 5.3 动态调整规则（规则引擎）

- 周期结束且打卡 ≥3 条时触发。
- `completion_rate < 0.5` 或 `fatigue_score ≥ 8` → 下一周期频率 −1、强度降一档。
- `completion_rate > 0.9` 且 `fatigue_score ≤ 4` → 频率 +1（上限 6）、强度升一档。
- 体重趋势与目标方向一致 → 维持；背离 → 提示复查饮食/目标。

---

## 6. 安全与性能

- 密码 bcrypt 哈希；JWT 24h 过期；CORS 白名单仅允许前端源。
- SQLAlchemy 参数化查询防注入；Pydantic 严格校验输入。
- 模型常驻内存避免每次加载；推荐接口 p95 ≤ 500ms。
- 前端图表数据按周/月聚合，后端返回聚合结果减少传输。

---

## 7. 备选方案与决策

| 方案 | 说明 | 决策 |
|------|------|------|
| 协同过滤 / 规则(BMI) | 开题报告指出其个性化不足 | 未采用，改随机森林多分类 |
| XGBoost / GBDT | 性能相近 | 未采用，论文选题锁定随机森林便于特征重要性分析 |
| Django 后端 | 全栈重 | 未采用，FastAPI 异步 + 自动 Swagger 更轻量 |
| 模型在线重训练 | 复杂度高、数据量不足 | 未采用，v1 采用离线训练 + 规则动态调整 |

---

## 8. 目录结构（建议）

```
SmartExercise/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI 入口 + CORS + 路由注册
│   │   ├── config.py          # 配置（DB/密钥）
│   │   ├── models/            # SQLAlchemy 模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── api/               # 路由
│   │   ├── services/          # 业务逻辑 + 推理 + 调整规则
│   │   └── core/              # 安全/依赖
│   ├── ml/                    # 训练脚本 + 预处理 + 模型文件
│   ├── data/                  # 数据集 + 问卷
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── views/             # 页面
    │   ├── components/        # 组件
    │   ├── api/               # Axios 封装
    │   ├── stores/            # Pinia
    │   └── router/
    └── package.json
```
