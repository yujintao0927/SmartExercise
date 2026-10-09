# SmartExercise 健身计划推荐系统

基于机器学习的健身计划推荐系统。系统以性别、年龄、身高、体重、运动目标、运动基础、每周可用时间、饮食偏好、运动伤病共 9 项特征为输入，采用随机森林算法输出训练目标、每周训练频率、动作组合、单次训练时长、训练强度、训练周期共 6 类推荐结果，并提供训练记录管理、动态调整建议与数据可视化功能。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3.10+ / FastAPI / SQLAlchemy / scikit-learn / PyJWT |
| 前端 | Vue 3 / Vite / Vue Router / Pinia / Axios / ECharts |
| 数据库 | SQLite（默认）/ MySQL（可切换） |

## 目录结构

```
SmartExercise/
├── backend/                 # 后端
│   ├── app/                 # FastAPI 应用（配置/模型/路由/服务）
│   ├── ml/                  # 数据处理与模型训练脚本
│   ├── tests/               # pytest 单元测试
│   ├── seed.py              # 动作库与计划模板种子数据
│   └── requirements.txt
├── frontend/                # 前端（Vue 3 + Vite）
│   └── src/
│       ├── api/             # Axios 封装
│       ├── router/          # 路由与登录守卫
│       ├── stores/          # Pinia 状态
│       ├── views/           # 页面
│       └── components/      # 布局组件
├── docs/                    # 论文与答辩文档
└── .claude/specs/           # 需求/设计/任务规范
```

## 环境要求

- Python 3.10 及以上
- Node.js 18 及以上
- npm（随 Node 安装）
- 无需联网下载数据集（预训练模型已随仓库分发）

## 快速启动

### 一、后端启动

1. 进入后端目录，创建并激活虚拟环境：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. 安装依赖：

```powershell
pip install -r requirements.txt
```

> 若下载慢，可先使用国内镜像：
> `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

3. 初始化动作库、计划模板与默认管理员账号：

```powershell
python seed.py
```

> 默认管理员账号：用户名 `admin`，密码 `admin123`（登录后进入管理端）。

4. 启动后端服务：

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

启动成功后访问接口文档：<http://127.0.0.1:8000/docs>

> 预训练模型已随仓库分发在 `backend/data/processed/model.joblib`，普通使用**无需**重新训练。仅当你需要更换数据集或调整模型时才需执行「开发者进阶：数据与模型训练」。

### 二、前端启动

1. 进入前端目录，安装依赖：

```powershell
cd frontend
npm install
```

> 若下载慢，可先设置国内镜像：`npm config set registry https://registry.npmmirror.com`

2. 启动开发服务器：

```powershell
npm run dev
```

启动成功后访问：<http://localhost:5173/>

### 三、访问系统

1. 打开 <http://localhost:5173/>，在登录页切换到「注册」，创建账号。
2. 登录后进入「画像」页，填写 9 项身体与习惯特征。
3. 保存后自动跳转「推荐」页，点击「生成推荐」查看训练计划。
4. 在「训练」页打卡，在「仪表盘」页查看完成率与体重趋势。

## 开发者进阶：数据与模型训练

> **普通使用者无需执行本节。** 预训练模型已随仓库分发在 `backend/data/processed/model.joblib`，直接按「快速启动」即可运行系统。
>
> 仅当你需要更换数据集、调整特征或重新调参时才需要重训。数据文件（`data/raw/`、`data/processed/`）与中间产物（`*.csv`、`train.joblib` 等）被 `.gitignore` 忽略，重训需先按以下顺序准备数据。

所有命令均需在 `backend` 目录下执行。

### 1. 下载公开数据集

将以下两个真实数据集下载到 `backend/data/raw/`：

```powershell
New-Item -ItemType Directory -Force -Path data\raw | Out-Null
curl.exe -L -o data\raw\meal_plan_exercise.csv "https://cdn.jsdelivr.net/gh/mehreengillani/DATA607@main/GYM.csv"
curl.exe -L -o data\raw\gym_members_exercise_tracking.csv "https://cdn.jsdelivr.net/gh/JaydeeJan/Exercise-Calories-Analysis@main/gym_members_exercise_tracking.csv"
```

### 2. 生成模拟问卷与身体素质数据

```powershell
python -m ml.make_mock_data
```

生成 `survey.csv`（500 条问卷样本）与 `body_performance.csv`（13393 条身体素质占位数据）。

### 3. 数据清洗

```powershell
python -m ml.preprocess
```

对四套数据做去重、缺失填充与异常值裁剪，输出到 `data/processed/`。

### 4. 构建训练集与特征编码

```powershell
python -m ml.build_dataset
```

按 9 特征规则引擎采样生成 80000 条训练样本，完成编码并保存到 `data/processed/train.joblib`。

### 5. 训练模型

```powershell
python -m ml.train_model
```

执行 SMOTE 类别平衡 + 随机森林网格搜索调优，保存模型到 `data/processed/model.joblib`。

> 说明：训练集由规则引擎生成，模型会精确拟合该规则映射（测试集加权 F1 ≈ 1.0）。若需真实泛化表现，请替换为真实问卷数据后重训。

## 配置说明

### 数据库切换

后端默认使用 SQLite，数据库文件为 `backend/smart_exercise.db`（自动创建，已被 `.gitignore` 忽略）。

切换到 MySQL 时，设置环境变量 `DATABASE_URL`（PowerShell）：

```powershell
$env:DATABASE_URL = "mysql+pymysql://root:密码@localhost:3306/smart_exercise"
```

连接串格式：`mysql+pymysql://用户名:密码@主机:端口/数据库名`。使用前需先在 MySQL 中创建数据库 `smart_exercise`，并确保 `pymysql` 已安装（已在 `requirements.txt` 中）。

### JWT 密钥

认证使用 JWT，密钥通过环境变量 `SECRET_KEY` 配置。生产环境务必设置强密钥：

```powershell
$env:SECRET_KEY = "你的随机强密钥（至少 32 字节）"
```

未设置时使用开发默认值，仅用于本地调试。

### 前端接口地址

前端请求后端的地址在 `frontend/src/api/index.js` 中：

```js
const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api' })
```

若后端更换主机或端口，需同步修改此地址。

### CORS 白名单

跨域白名单在后端 `backend/app/main.py` 中配置：

```python
allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
```

前端更换端口时，需将新地址加入白名单。

## 运行测试

在 `backend` 目录下执行：

```powershell
python -m pytest tests/ -v
```

共 13 个单元测试，覆盖安全工具、规则引擎、动态调整、模型推理一致性与 Pydantic 校验。

## 常见问题

- **后端启动报「模型文件不存在」**：预训练模型应随仓库位于 `backend/data/processed/model.joblib`，若缺失请确认 clone 完整，或按「开发者进阶：数据与模型训练」重新生成。
- **`ModuleNotFoundError: No module named 'ml'`**：需在 `backend` 目录下运行脚本，且使用 `python -m ml.xxx` 方式。
- **前端请求后端报 CORS 错误**：确认前端地址在后端 CORS 白名单中，且前端 `baseURL` 与后端实际地址一致。
- **数据下载失败**：仅在按「开发者进阶」重训时才会下载数据集。网络无法直连 GitHub 时，改用国内镜像或手动下载后放入 `backend/data/raw/`，文件名保持上述一致。
- **MySQL 连接失败**：确认 `DATABASE_URL` 连接串正确、MySQL 服务已启动、目标数据库已创建。
