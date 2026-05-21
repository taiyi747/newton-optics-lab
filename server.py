#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI 服务入口 - 牛顿环综合实验平台后端

启动方式:
    python server.py

访问:
    http://localhost:8000

API 文档:
    http://localhost:8000/docs
"""

import os
import sys

# 设置 matplotlib 使用非 GUI 后端 (必须在导入 matplotlib 之前)
import matplotlib
matplotlib.use('agg')

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles

# 创建 FastAPI 应用
app = FastAPI(
    title="牛顿环综合实验平台 API",
    description="光学实验教学辅助系统接口",
    version="2.0.0",
)

# CORS 配置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入 API 路由
from lib.api import demo_router, data_router, ai_router

# 注册 API 路由
app.include_router(demo_router, prefix="/api", tags=["演示实验"])
app.include_router(data_router, prefix="/api", tags=["数据处理"])
app.include_router(ai_router, tags=["AI 助手"])

# 暂时不让后端打包/挂载前端静态资源。
# frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
# if os.path.exists(frontend_dir):
#     app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "newton-rings-api"}


if __name__ == "__main__":
    # 检测是否为 Nuitka 打包后的环境
    if '__compiled__' in globals():
        # 打包后：直接传递 app 对象，禁用重载
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
        )
    else:
        # 开发模式：使用字符串引用，启用热重载
        uvicorn.run(
            "server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
        )
