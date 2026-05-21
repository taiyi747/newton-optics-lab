# -*- coding: utf-8 -*-
"""
演示实验 API - 牛顿环模拟计算接口
"""

from fastapi import APIRouter
from pydantic import BaseModel

from lib.services.demo_service import (
    calculate_normal_newton_rings,
    calculate_truncated_newton_rings,
    calculate_convex_concave_contact,
    calculate_convex_convex_contact,
    calculate_convex_concave_noncontact,
    calculate_convex_convex_noncontact,
)

router = APIRouter()


# ==================== 请求参数模型 ====================

class DemoNormalParams(BaseModel):
    """普通牛顿环参数"""
    wavelength_nm: float
    radius_m: float
    spacing_nm: float = 0
    refractive_n: float = 1.0


class DemoTruncatedParams(BaseModel):
    """截顶式牛顿环参数"""
    wavelength_nm: float
    radius_m: float
    height_nm: float
    refractive_n: float = 1.0


class DemoConvexConcaveContactParams(BaseModel):
    """平凸-平凹透镜接触式参数"""
    wavelength_nm: float
    R1_m: float
    R2_m: float
    refractive_n: float = 1.0


class DemoConvexConvexContactParams(BaseModel):
    """双平凸透镜接触式参数"""
    wavelength_nm: float
    R1_m: float
    R2_m: float
    refractive_n: float = 1.0


class DemoConvexConcaveNoncontactParams(BaseModel):
    """平凸-平凹透镜非接触式参数"""
    wavelength_nm: float
    R1_m: float
    R2_m: float
    spacing_nm: float
    refractive_n: float = 1.0


class DemoConvexConvexNoncontactParams(BaseModel):
    """双平凸透镜非接触式参数"""
    wavelength_nm: float
    R1_m: float
    R2_m: float
    spacing_nm: float
    refractive_n: float = 1.0


# ==================== API 路由 ====================

@router.post("/demo_normal")
async def demo_normal(params: DemoNormalParams):
    """
    普通牛顿环计算

    物理原理:
    - 公式: r_k = sqrt(k * λ * R)
    - 光强: I = 2(1 - cos(4πnd/λ))
    """
    return calculate_normal_newton_rings(
        wavelength_nm=params.wavelength_nm,
        radius_m=params.radius_m,
        spacing_nm=params.spacing_nm,
        refractive_n=params.refractive_n
    )


@router.post("/demo_truncated")
async def demo_truncated(params: DemoTruncatedParams):
    """
    截顶式牛顿环计算

    复用普通牛顿环计算逻辑
    """
    return calculate_truncated_newton_rings(
        wavelength_nm=params.wavelength_nm,
        radius_m=params.radius_m,
        height_nm=params.height_nm,
        refractive_n=params.refractive_n
    )


@router.post("/demo_convex_concave_contact")
async def demo_convex_concave_contact(params: DemoConvexConcaveContactParams):
    """
    平凸-平凹透镜接触式牛顿环计算

    物理原理:
    - 曲率差: Δ = 1/R1 - 1/R2
    - 光程差: d = r²/2 * Δ
    """
    return calculate_convex_concave_contact(
        wavelength_nm=params.wavelength_nm,
        R1_m=params.R1_m,
        R2_m=params.R2_m,
        refractive_n=params.refractive_n
    )


@router.post("/demo_convex_convex_contact")
async def demo_convex_convex_contact(params: DemoConvexConvexContactParams):
    """
    双平凸透镜接触式牛顿环计算

    物理原理:
    - 曲率差: Δ = 1/R1 + 1/R2
    """
    return calculate_convex_convex_contact(
        wavelength_nm=params.wavelength_nm,
        R1_m=params.R1_m,
        R2_m=params.R2_m,
        refractive_n=params.refractive_n
    )


@router.post("/demo_convex_concave_noncontact")
async def demo_convex_concave_noncontact(params: DemoConvexConcaveNoncontactParams):
    """
    平凸-平凹透镜非接触式牛顿环计算

    物理原理:
    - 光程差: d = r²/2 * (1/R1 - 1/R2) + h
    """
    return calculate_convex_concave_noncontact(
        wavelength_nm=params.wavelength_nm,
        R1_m=params.R1_m,
        R2_m=params.R2_m,
        spacing_nm=params.spacing_nm,
        refractive_n=params.refractive_n
    )


@router.post("/demo_convex_convex_noncontact")
async def demo_convex_convex_noncontact(params: DemoConvexConvexNoncontactParams):
    """
    双平凸透镜非接触式牛顿环计算
    """
    return calculate_convex_convex_noncontact(
        wavelength_nm=params.wavelength_nm,
        R1_m=params.R1_m,
        R2_m=params.R2_m,
        spacing_nm=params.spacing_nm,
        refractive_n=params.refractive_n
    )
