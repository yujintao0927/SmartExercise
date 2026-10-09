from fastapi import FastAPI

app = FastAPI(
    title="SmartExercise 健身计划推荐系统",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "SmartExercise API 运行中"}
