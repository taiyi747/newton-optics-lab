# -*- coding: utf-8 -*-
"""
API 路由模块 - 物理光学综合实验平台 FastAPI 接口
"""

from .demo import router as demo_router
from .data import router as data_router
from .ai import router as ai_router

__all__ = [
    'demo_router',
    'data_router',
    'ai_router',
]
