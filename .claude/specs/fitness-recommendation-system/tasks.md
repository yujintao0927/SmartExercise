# 基于机器学习的健身计划推荐系统 — 任务清单

> 版本：v1.1
> 关联：requirements.md / design.md
> 任务约定：`T-` 为代码实现任务，`P-` 为论文写作里程碑（与开发并行推进）；`T-Xa` 为 `T-X` 的补充任务。
> 状态流转：`pending → in_progress → completed`，且需 `Wired` 与 `Verified` 到位才算真正完成。
> **开发约定**：每个 T/P 任务完成后执行一次 git 提交（commit message 采用「类型: 任务号 + 简述」）；前端任务（T-16 起）使用提供的 frontend-design / frontend-skill。

## 与开题进度安排对齐

| 开题阶段 | 时间 | 对应任务 |
|----------|------|----------|
| 可行性/需求分析 | 08.24–09.20 | T-0 ~ T-2 |
| 系统设计 | 09.21–10.18 | T-3 ~ T-15a（含 design.md 落地） |
| 系统实现 | 10.19–11.08 | T-16 ~ T-22 |
| 系统测试 | 11.09–11.15 | T-23 ~ T-25 |
| 准备答辩 | 11.16–12.13 | P-6 ~ P-7 |

---

## Phase 0：项目初始化与环境搭建

### T-0：初始化项目结构与开发环境
- **Status**: completed
- **Wired**: n/a
- **Verified**: yes
- **Requirements**: infrastructure
- **Description**: 按 design.md §8 建立 backend / frontend 目录；初始化 git 仓库；后端 requirements.txt（fastapi、uvicorn、sqlalchemy、pymysql、pydantic、pyjwt、scikit-learn、imbalanced-learn、pandas、joblib）；前端 Vite 脚手架（Vue 3 + Pinia + Router + Axios + ECharts）。
- **Acceptance**:
  - `uvicorn app.main:app` 可启动并访问 `/docs`
  - `npm run dev` 可启动前端并显示默认页
  - 首次 git 提交完成
- **Dependencies**: none

### T-1：配置数据库连接
- **Status**: completed
- **Wired**: n/a
- **Verified**: yes
- **Requirements**: infrastructure
- **Description**: 编写 config.py 与 SQLAlchemy engine/session；开发阶段默认 SQLite（免服务），MySQL 通过环境变量 DATABASE_URL 切换；确保可连通。
- **Acceptance**: 后端可建立数据库连接，`Base.metadata` 无报错。
- **Dependencies**: T-0

---

## Phase 1：数据处理与模型训练

### T-2：数据采集与特征字典定义
- **Status**: completed
- **Wired**: n/a
- **Verified**: yes
- **Requirements**: US-2, US-3
- **Description**: 下载三套 Kaggle 数据集（MealPlan 80k、Gym Members 973 已真实下载；Body Performance 因 Kaggle 认证/网络限制用占位数据，正式需 Kaggle）；生成问卷星 CSV 模拟数据（survey.csv 500 条）；编写 9 特征标准字典（backend/ml/feature_dictionary.py）。
- **Acceptance**: 三套数据 + 问卷 CSV 落盘，特征字典成文。
- **Dependencies**: T-0

### T-3：数据清洗与多源融合
- **Status**: completed
- **Wired**: n/a
- **Verified**: yes
- **Requirements**: US-3, NFR-数据质量
- **Description**: 编写 backend/ml/preprocess.py，做缺失填充、异常值裁剪（winsorize）、去重；MealPlan（80k，实为 16 规则组合重复的标签主数据集）保留原始规模，其余数据集去重；输出 data/processed/ 清洗后数据。
- **Acceptance**: 生成统一特征矩阵，可用样本 ≥ 89,000 条（实际 94,866）。
- **Dependencies**: T-2

### T-4：特征工程与编码
- **Status**: completed
- **Wired**: n/a
- **Verified**: yes
- **Requirements**: US-3
- **Description**: 编写 rule_engine.py（规则引擎 9特征→6输出，解决 MealPlan 仅 3 特征的数据缺口）+ build_dataset.py（采样 80k 训练样本）；派生 BMI；分类 Label 编码、injury 多标签 one-hot、数值标准化；保存编码器到 data/processed/train.joblib。
- **Acceptance**: 编码后可复现，训练/推理编码一致（X 80000×15，编码器含 label/injury_mlb/scaler）。
- **Dependencies**: T-3

### T-5：SMOTE 类别平衡
- **Status**: completed
- **Wired**: n/a
- **Verified**: yes
- **Requirements**: US-3, NFR-数据质量
- **Description**: 训练集目标分布不平衡（减脂 32143 vs 保持健康 7871），引入 SMOTE 过采样（k=5）平衡。
- **Acceptance**: 各类别样本量趋于平衡（SMOTE 后各 32143），无类别丢失。
- **Dependencies**: T-4

### T-6：训练随机森林并网格搜索调优
- **Status**: completed
- **Wired**: n/a
- **Verified**: yes
- **Requirements**: US-3
- **Description**: 训练 5 个 RandomForestClassifier（target_goal 用 GridSearchCV 调优，其余默认参数）；GridSearchCV 调优 n_estimators、max_depth。
- **Acceptance**: 输出最优超参组合（max_depth=10, n_estimators=50），模型可序列化保存。
- **Dependencies**: T-5

### T-7：模型评估与特征重要性
- **Status**: completed
- **Wired**: n/a
- **Verified**: yes
- **Requirements**: US-3, NFR-模型质量
- **Description**: 以准确率、加权 F1 评估 5 个输出；输出特征重要性排序（goal 93% 主导）；保存 model.joblib + 编码器 + feature_importance.csv。
- **Acceptance**: 加权 F1 达可接受阈值（target_goal=1.0000）；生成特征重要性数据。
- **Dependencies**: T-6

---

## Phase 2：后端 API

### T-8：定义 SQLAlchemy 模型
- **Status**: completed
- **Wired**: no
- **Verified**: yes
- **Requirements**: US-1, US-2, US-4, US-6
- **Description**: 实现 design.md §2.2 的 7 张表（user、user_profile、recommendation_record、training_record、body_metric、exercise、plan_template）；`injury` 用 JSON 存多选部位数组。
- **Acceptance**: 建表迁移成功，外键关系正确（7 张表已创建）。
- **Dependencies**: T-1

### T-8a：动作库与计划模板种子数据
- **Status**: completed
- **Wired**: no
- **Verified**: yes
- **Requirements**: US-3
- **Description**: 初始化 exercise 动作字典与 plan_template 计划模板（按 目标×强度 组合），供推荐动作组合查询。
- **Acceptance**: 各 目标×强度 组合存在模板，动作可关联查询（44 动作、15 模板）。
- **Dependencies**: T-8

### T-9：定义 Pydantic Schemas
- **Status**: completed
- **Wired**: no
- **Verified**: yes
- **Requirements**: US-2, US-3, US-4
- **Description**: 定义请求/响应模型（app/schemas.py），包含 9 特征（injury 为多选列表，用 Literal + field_validator 校验）与 6 输出的字段校验。
- **Acceptance**: 非法输入（越界/缺失/「无」与其他部位同时选中）返回 422（pytest 4 通过）。
- **Dependencies**: T-8

### T-10：实现认证路由与 JWT
- **Status**: completed
- **Wired**: yes
- **Verified**: yes
- **Requirements**: US-1
- **Description**: 注册/登录接口；bcrypt 哈希；签发 24h JWT；鉴权依赖；`role` 字段写入。
- **Acceptance**: 注册成功、重复用户名 409、正确登录 200、错误凭证 401。
- **Dependencies**: T-8, T-9

### T-11：实现画像路由
- **Status**: completed
- **Wired**: yes
- **Verified**: yes
- **Requirements**: US-2
- **Description**: PUT/GET `/api/profile`，保存/更新画像（含多选 injury）。
- **Acceptance**: 画像可写可读，更新后标记推荐待重算。
- **Dependencies**: T-9, T-10

### T-12：实现推荐路由与推理服务
- **Status**: completed
- **Wired**: yes
- **Verified**: yes
- **Requirements**: US-3
- **Description**: 加载模型常驻内存；`POST /api/recommend` 推理并保存记录（动作组合由 plan_template 查询组装）；`GET /api/recommend/history`。
- **Acceptance**: 返回 6 类结果并带 model_version；模型未加载时返回友好错误。
- **Dependencies**: T-7, T-8a, T-11

### T-13：实现训练记录路由
- **Status**: completed
- **Wired**: yes
- **Verified**: yes
- **Requirements**: US-4
- **Description**: 打卡写入与历史查询。
- **Acceptance**: 记录可写、倒序查询。
- **Dependencies**: T-9, T-10

### T-14：实现仪表盘与身体指标路由
- **Status**: completed
- **Wired**: yes
- **Verified**: yes
- **Requirements**: US-6
- **Description**: 体重录入；完成率/体重趋势聚合接口。
- **Acceptance**: 返回按周/月聚合的序列数据。
- **Dependencies**: T-13

### T-15：实现动态调整规则引擎
- **Status**: completed
- **Wired**: yes
- **Verified**: yes
- **Requirements**: US-5
- **Description**: 按 design.md §5.3 规则，周期结束且打卡 ≥3 时给出频率/强度调整建议。
- **Acceptance**: 低完成率/高疲劳触发降档，高完成率/低疲劳触发升档。
- **Dependencies**: T-13

### T-15a：实现管理员路由
- **Status**: completed
- **Wired**: yes
- **Verified**: yes
- **Requirements**: 最小管理员
- **Description**: 新增 `require_admin` 鉴权依赖；`GET /api/admin/users` 用户列表、`GET /api/admin/model` 模型版本与加载状态。
- **Acceptance**: 非管理员访问返回 403，管理员可查看用户列表与模型信息。
- **Dependencies**: T-8, T-11

---

## Phase 3：前端（使用 frontend-design / frontend-skill）

### T-16：前端基础框架
- **Status**: completed
- **Wired**: yes
- **Verified**: yes
- **Requirements**: infrastructure
- **Description**: 路由（vue-router + 守卫）、Pinia、Axios 封装（JWT 拦截器 + 统一错误处理）、布局组件；整体视觉设计应用 frontend-design skill（深色工业力量感 + 酸性绿强调，Anton/Outfit 字体）。
- **Acceptance**: 路由守卫对未登录访问跳转登录页。
- **Dependencies**: T-0

### T-17：登录/注册页面
- **Status**: completed
- **Wired**: yes
- **Verified**: yes
- **Requirements**: US-1
- **Description**: 登录与注册表单（LoginView.vue），接入 /auth/login 与 /auth/register，保存 token；登录/注册切换。
- **Acceptance**: 登录成功跳转首页，失败显示错误提示（错误文本来自后端 detail）。
- **Dependencies**: T-10, T-16

### T-18：画像录入页面
- **Status**: pending
- **Wired**: no
- **Verified**: no
- **Requirements**: US-2
- **Description**: 9 特征表单（下拉/数字输入，injury 多选），内联校验。
- **Acceptance**: 合法值提交成功，非法值内联报错。
- **Dependencies**: T-11, T-16

### T-19：推荐结果展示页面
- **Status**: pending
- **Wired**: no
- **Verified**: no
- **Requirements**: US-3
- **Description**: 展示 6 类推荐结果，含动作组合卡片。
- **Acceptance**: 点击「生成推荐」后展示结果，加载态与错误态正常。
- **Dependencies**: T-12, T-16

### T-20：训练打卡页面
- **Status**: pending
- **Wired**: no
- **Verified**: no
- **Requirements**: US-4, US-5
- **Description**: 提交完成率、疲劳评分、反馈；展示历史记录与调整建议。
- **Acceptance**: 打卡可提交；周期结束显示调整建议。
- **Dependencies**: T-13, T-15, T-16

### T-21：仪表盘可视化页面
- **Status**: pending
- **Wired**: no
- **Verified**: no
- **Requirements**: US-6
- **Description**: ECharts 绘制完成率与体重趋势，支持周/月切换。
- **Acceptance**: 图表随接口数据正确渲染。
- **Dependencies**: T-14, T-16

### T-21a：管理员页面
- **Status**: pending
- **Wired**: no
- **Verified**: no
- **Requirements**: 最小管理员
- **Description**: 管理端页面，展示用户列表与当前模型版本信息。
- **Acceptance**: 管理员登录可见入口，页面数据正确渲染。
- **Dependencies**: T-15a, T-16

---

## Phase 4：集成联调

### T-22：前后端联调
- **Status**: pending
- **Wired**: no
- **Verified**: no
- **Requirements**: US-1 ~ US-6
- **Description**: 配置 CORS 白名单；核对各页面接口请求/响应字段一致；修复跨域与数据解析问题。
- **Acceptance**: 全链路「注册→画像→推荐→打卡→可视化」无报错走通。
- **Dependencies**: T-17 ~ T-21a

---

## Phase 5：测试

### T-23：后端单元测试
- **Status**: pending
- **Wired**: n/a
- **Verified**: no
- **Requirements**: US-1, US-3, US-5
- **Description**: pytest 覆盖认证、画像校验、规则引擎；使用 `unittest.mock.patch` 隔离 DB/模型。
- **Acceptance**: 关键用例通过，覆盖核心逻辑。
- **Dependencies**: T-15a, T-22

### T-24：模型与接口测试
- **Status**: pending
- **Wired**: n/a
- **Verified**: no
- **Requirements**: NFR-性能, NFR-模型质量
- **Description**: 验证推理一致性（相同画像结果稳定）；压测推荐接口响应时间。
- **Acceptance**: 推荐 p95 ≤ 500ms；相同输入输出一致。
- **Dependencies**: T-12

### T-25：端到端手工测试
- **Status**: pending
- **Wired**: n/a
- **Verified**: no
- **Requirements**: US-1 ~ US-6
- **Description**: 按用户故事逐条手工回归，记录缺陷并修复。
- **Acceptance**: 所有 EARS 验收标准人工通过。
- **Dependencies**: T-22

---

## Phase 6：论文写作里程碑（与开发并行）

> P 任务可随对应 T 任务完成即启动，不必等全部开发结束。

### P-1：绪论与国内外研究现状
- **Status**: pending
- **Wired**: n/a
- **Verified**: no
- **Requirements**: 论文
- **Description**: 撰写选题背景、目的意义、国内外研究现状与文献综述。
- **Acceptance**: 引用开题报告参考文献 [1]–[10]，完成初稿。
- **Dependencies**: T-2

### P-2：需求分析与系统设计章节
- **Status**: pending
- **Wired**: n/a
- **Verified**: no
- **Requirements**: 论文
- **Description**: 将 requirements.md 与 design.md 转写为论文第 2–3 章（功能/非功能需求、架构、数据库设计，含 7 表与 ER 图）。
- **Acceptance**: 章节含架构图、ER 图、数据表说明。
- **Dependencies**: P-1

### P-3：数据预处理与模型构建章节
- **Status**: pending
- **Wired**: n/a
- **Verified**: no
- **Requirements**: 论文
- **Description**: 撰写数据清洗、特征工程（含 injury 多标签编码）、SMOTE、随机森林训练与调优；附特征重要性结果。
- **Acceptance**: 含实验数据与图表（对应 T-3 ~ T-7）。
- **Dependencies**: T-7, P-2

### P-4：系统实现章节
- **Status**: pending
- **Wired**: n/a
- **Verified**: no
- **Requirements**: 论文
- **Description**: 描述前后端关键模块实现、核心代码与界面截图。
- **Acceptance**: 覆盖 6 大功能模块（对应 T-10 ~ T-22）。
- **Dependencies**: T-22, P-2

### P-5：系统测试与结果分析章节
- **Status**: pending
- **Wired**: n/a
- **Verified**: no
- **Requirements**: 论文
- **Description**: 模型评估结果分析、系统功能测试、性能测试结论。
- **Acceptance**: 含准确率/加权 F1 表格与测试用例表（对应 T-23 ~ T-25）。
- **Dependencies**: T-24, T-25, P-3

### P-6：摘要、结论、参考文献与致谢
- **Status**: pending
- **Wired**: n/a
- **Verified**: no
- **Requirements**: 论文
- **Description**: 中英文摘要、结论与展望、规范参考文献、致谢。
- **Acceptance**: 摘要含方法+结果+结论三要素。
- **Dependencies**: P-5

### P-7：格式排版、查重与答辩材料
- **Status**: pending
- **Wired**: n/a
- **Verified**: no
- **Requirements**: 论文
- **Description**: 按学院模板排版、降重、制作答辩 PPT 与功能框图。
- **Acceptance**: 通过查重与格式审查，PPT 完成。
- **Dependencies**: P-6

---

## 追溯矩阵

| 需求 | 任务 |
|------|------|
| US-1 注册登录 | T-8, T-9, T-10, T-17 |
| US-2 画像录入 | T-2, T-8, T-9, T-11, T-18 |
| US-3 智能推荐 | T-2 ~ T-7, T-8a, T-12, T-19 |
| US-4 训练记录 | T-8, T-9, T-13, T-20 |
| US-5 动态调整 | T-15, T-20 |
| US-6 可视化 | T-8, T-14, T-21 |
| 动作库字典表 | T-8, T-8a |
| 最小管理员 | T-8, T-15a, T-21a |
| 集成 | T-22 |
| 测试 | T-23, T-24, T-25 |
| 论文 | P-1 ~ P-7 |

## 任务统计（初始）

| 类别 | 数量 |
|------|------|
| 代码任务（T） | 29 |
| 论文里程碑（P） | 7 |
| 合计 | 36 |
