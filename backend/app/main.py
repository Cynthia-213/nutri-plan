from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Nutri-Plan API",
    description="个人饮食运动热量收支平衡系统的后端API",
    version="1.0.0"
)

# --- 中间件配置 ---

# 配置 CORS (跨源资源共享)
# 允许所有来源，所有方法，所有头部，用于开发环境。
# 在生产环境中，应该限制 origins 的范围。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# --- 根路由 ---
@app.get("/", tags=["Root"])
def read_root():
    """
    根路径，返回一个欢迎信息。
    """
    return {"message": "Welcome to the Nutri-Plan!"}

# --- 包含主API路由 ---
# 将所有在 api_router 中定义的路由包含进来，并添加统一的前缀 /api
app.include_router(api_router, prefix="/api")

# --- 应用启动时的附加逻辑 (可选) ---
# @app.on_event("startup")
# async def startup_event():
#     print("Application is starting up...")

# @app.on_event("shutdown")
# async def shutdown_event():
#     print("Application is shutting down...")
