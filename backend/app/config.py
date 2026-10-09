"""应用配置。"""
import os

# 数据库连接地址：开发阶段默认使用 SQLite（免服务、免 Docker），
# 联调/部署时通过环境变量 DATABASE_URL 切换为 MySQL，例如：
#   mysql+pymysql://root:password@localhost:3306/smart_exercise
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smart_exercise.db")

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me-please-set-env-var")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时
