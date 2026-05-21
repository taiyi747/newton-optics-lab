# -*- coding: utf-8 -*-
"""
数据处理 API - 实验数据分析接口
"""

from fastapi import APIRouter
from pydantic import BaseModel

from lib.services.data_service import process_data as process_data_impl

router = APIRouter()


# ==================== 请求参数模型 ====================

class ProcessDataParams(BaseModel):
    """数据处理参数"""
    csv_content: str
    wavelength_nm: float
    refractive_n: float = 1.0


# ==================== API 路由 ====================

@router.post("/process_data")
async def process_data(params: ProcessDataParams):
    """
    处理实验数据，计算曲率半径

    计算原理:
    1. 计算直径: D = |x_左 - x_右|
    2. 直径平方: D²
    3. 线性拟合: D² = 4Rλk + b
    4. 求解曲率半径: R = slope / (4λ)

    CSV 格式:
    - 第一行: 标题 + 级数值（如 40, 35, 30, 25, 20, 15, 10, 5）
    - 第二行: "左" 或 "Left" + 左侧读数（mm）
    - 第三行: "右" 或 "Right" + 右侧读数（mm）
    """
    return process_data_impl(
        csv_content=params.csv_content,
        wavelength_nm=params.wavelength_nm,
        refractive_n=params.refractive_n
    )
