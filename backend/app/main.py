"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models, routers, services  # noqa: F401  导入 models 以注册建表
from .database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    services.load_model()  # 启动时预加载模型
    yield


app = FastAPI(
    title="SmartExercise 健身计划推荐系统",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS：允许前端 Vue dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(routers.router)


@app.get("/")
def root():
    return {"message": "SmartExercise API 运行中"}
