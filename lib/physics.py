# -*- coding: utf-8 -*-
"""
牛顿环物理计算核心模块

本模块提供牛顿环干涉现象的物理计算功能，包括：
- 光程差计算（核心物理量）
- 光强分布计算（干涉图样）
- 牛顿环半径计算（测量应用）
- 一维/二维数据生成（可视化支持）

物理原理：
    牛顿环是由平凸透镜和平板玻璃（或另一透镜）之间形成的空气薄膜
    产生的等厚干涉现象。当单色光垂直入射时，空气薄膜上下表面
    反射的光产生干涉，形成明暗相间的同心圆环。

    基本公式：
    - 空气薄膜厚度: h = r²/(2R)
    - 光程差: δ = 2h + λ/2 = r²/R + λ/2（考虑半波损失）
    - 明纹条件: δ = kλ (k=1,2,3,...)
    - 暗纹条件: δ = (k+1/2)λ
    - 第k级环半径: r_k = √(kλR)

模块依赖:
    - numpy: 数值计算

作者：[项目作者]
创建日期：[日期]
"""

import numpy as np


# ==================== 核心物理计算函数 ====================

def compute_optical_path_difference(r, R, curvature_difference=0.0, h=0.0):
    """
    计算空气薄膜干涉的光程差

    光程差是决定干涉条纹位置的核心物理量。本函数支持多种透镜组合配置，
    通过统一的公式计算任意位置的空气薄膜等效厚度。

    Args:
        r (float or ndarray): 径向位置，到干涉中心的距离，单位：米 (m)
            可以是标量或 numpy 数组，用于计算分布
        R (float): 参考曲率半径，单位：米 (m)
            在复合透镜系统中作为主要参考值
        curvature_difference (float): 组合曲率差，单位：1/米 (m⁻¹)
            - 单透镜/平板组合: 0（使用默认 R）
            - 凸-凹透镜组合: 1/R1 - 1/R2
            - 双凸透镜组合: 1/R1 + 1/R2
            默认值: 0.0
        h (float): 空气间隙高度（非接触式配置），单位：米 (m)
            两光学表面之间的最小距离，仅影响整体光程差
            默认值: 0.0（接触式）

    Returns:
        float or ndarray: 光程差序列，单位：米 (m)
            值等于等效空气薄膜厚度的两倍（考虑反射相长干涉）

    Physics:
        光程差计算公式：
        1. 当 curvature_difference ≠ 0 时（复合透镜系统）:
           δ = (r²/2) × curvature_difference + h
        2. 当 curvature_difference = 0 时（单透镜/平板）:
           δ = r²/(2R) + h

        注意：本函数返回的是空气薄膜等效厚度，
        实际光程差应为 2δ（上下表面反射光的光程差）

    Examples:
        # 计算距中心1mm处的光程差（单透镜）
        >>> delta = compute_optical_path_difference(1e-3, 1.0)
        >>> print(delta)  # 约 5e-7 m

        # 双凸透镜组合的光程差
        >>> curvature = 1/0.5 + 1/0.8  # R1=0.5m, R2=0.8m
        >>> delta = compute_optical_path_difference(1e-3, 0.5, curvature)
    """
    # 根据曲率差选择计算方式
    if curvature_difference != 0:
        # 复合透镜系统：使用曲率差公式
        d = (r**2 / 2) * curvature_difference
    else:
        # 单透镜/平板系统：使用基本公式
        d = r**2 / (2 * R)

    # 非接触式配置：加上间隙高度
    if h != 0:
        d = d + h

    return d


def compute_intensity(d, lam, n=1.0):
    """
    计算干涉光强分布

    根据光程差计算干涉条纹的相对光强。光强分布是周期性的函数，
    取决于光程差与波长的比值。

    Args:
        d (float or ndarray): 光程差（空气薄膜厚度的两倍），单位：米 (m)
            由 compute_optical_path_difference 计算得到
        lam (float): 入射光波长，单位：米 (m)
            典型值: 钠黄光 589.3e-9, 氦氖激光 632.8e-9
        n (float): 介质折射率，无量纲
            默认值: 1.0（空气）

    Returns:
        float or ndarray: 相对光强，无量纲
            范围: [0, 4]，对应暗纹到明纹

    Physics:
        干涉光强公式（双光束干涉）：
        I = I₁ + I₂ + 2√(I₁I₂)cos(Δφ)

        对于等振幅双光束：
        I = 2I₀(1 + cos(Δφ))

        相位差与光程差的关系：
        Δφ = 4πnd/λ （考虑两次反射）

        代入得：
        I = 2I₀(1 + cos(4πnd/λ))

        本函数返回: 2(1 - cos(4πnd/λ))
        该形式便于后续归一化和图像编码

    Note:
        - 光强最大值出现在 cos(...) = -1 时（明纹）
        - 光强最小值出现在 cos(...) = 1 时（暗纹）
        - 由于半波损失，中心（d=0）为暗斑
    """
    return 2 * (1 - np.cos(4 * np.pi * n * d / lam))


def compute_ring_radius(k, lam, R, n=1.0):
    """
    计算第k级牛顿环的半径

    这是牛顿环实验中测量曲率半径的理论基础。
    通过测量不同级次环的半径，可以精确计算透镜的曲率半径。

    Args:
        k (int or float): 牛顿环的级数（环序号）
            k = 1, 2, 3, ... 对应第1, 2, 3,... 级环
            注意：中心暗斑为第0级
        lam (float): 入射光波长，单位：米 (m)
        R (float): 透镜曲率半径，单位：米 (m)
        n (float): 介质折射率，无量纲
            默认值: 1.0（空气）

    Returns:
        float: 第k级牛顿环的半径，单位：米 (m)

    Physics:
        由明纹条件 δ = kλ 推导：
        r²/R = kλ
        r = √(kλR)

        考虑折射率时：
        r = √(kλR/n)

    Applications:
        曲率半径测量方法：
        1. 测量第m级和第n级环的半径 r_m 和 r_n
        2. 计算: R = (r_m² - r_n²) / ((m-n)λ)
        3. 这种方法消除了中心零点不确定性

    Examples:
        # 计算第10级牛顿环半径（钠光，R=1m）
        >>> r10 = compute_ring_radius(10, 589.3e-9, 1.0)
        >>> print(f"第10级环半径: {r10*1000:.3f} mm")  # 约 2.43 mm
    """
    return np.sqrt(k * lam * R / n)


# ==================== 一维/二维数据生成函数 ====================

def newtons_rings_1d(lam, R, n=1.0, h=0.0, curvature_diff=0.0, num_points=3000):
    """
    生成一维牛顿环光强分布数据

    计算沿径向的光强分布曲线，用于绘制光强-半径关系图。
    这对于分析干涉条纹的周期性和对比度非常有用。

    Args:
        lam (float): 入射光波长，单位：米 (m)
            典型值: 钠黄光 589.3e-9, 氦氖激光 632.8e-9
        R (float): 参考曲率半径，单位：米 (m)
        n (float): 介质折射率，无量纲，默认: 1.0
        h (float): 空气间隙高度，单位：米 (m)，默认: 0.0
        curvature_diff (float): 组合曲率差，单位: 1/米 (m⁻¹)，默认: 0.0
            详见 compute_optical_path_difference 的说明
        num_points (int): 采样点数，默认: 3000
            更多的点提供更高的分辨率，但计算时间更长

    Returns:
        tuple: (r, intensity, max_r)
            - r (ndarray): 径向坐标数组，单位：米 (m)，范围: [-max_r, max_r]
            - intensity (ndarray): 光强数组，无量纲，范围: [0, 4]
            - max_r (float): 最大计算半径，单位：米 (m)

    Physics:
        计算范围: ±√(50λR)，这保证了约50级干涉环的完整显示
        采样密度: 采样点在计算范围内均匀分布

    Applications:
        - 绘制径向光强分布曲线
        - 分析条纹对比度
        - 验证干涉理论计算

    Examples:
        # 计算钠黄光下的标准牛顿环
        >>> r, I, max_r = newtons_rings_1d(589.3e-9, 1.0)
        >>> print(f"计算范围: ±{max_r*1000:.2f} mm")
    """
    # 确定计算范围：包含约50级干涉环
    max_r = np.sqrt(50 * lam * R)

    # 生成径向采样点
    r = np.linspace(-max_r, max_r, num_points)

    # 计算光程差
    d = compute_optical_path_difference(r, R, curvature_diff, h)

    # 计算光强分布
    intensity = compute_intensity(d, lam, n)

    return r, intensity, max_r


def newtons_rings_2d(lam, R, n=1.0, h=0.0, curvature_diff=0.0,
                     levels=50, resolution=801):
    """
    生成二维牛顿环图像数据

    创建二维网格上的光强分布矩阵，用于生成牛顿环的干涉图样图像。
    这是可视化牛顿环现象的核心函数。

    Args:
        lam (float): 入射光波长，单位：米 (m)
        R (float): 参考曲率半径，单位：米 (m)
        n (float): 介质折射率，无量纲，默认: 1.0
        h (float): 空气间隙高度，单位：米 (m)，默认: 0.0
        curvature_diff (float): 组合曲率差，单位: 1/米 (m⁻¹)，默认: 0.0
            详见 compute_optical_path_difference 的说明
        levels (int): 显示的干涉环级数，默认: 50
            决定了图像的物理范围
        resolution (int): 网格分辨率（每边的像素数），默认: 801
            应为奇数以保证中心对称

    Returns:
        tuple: (X, Y, B, ym)
            - X (ndarray): 二维网格X坐标矩阵，单位：米 (m)
            - Y (ndarray): 二维网格Y坐标矩阵，单位：米 (m)
            - B (ndarray): 亮度矩阵，范围: [0, 255]，可直接用于图像编码
            - ym (float): 图像半宽度，单位：米 (m)

    Physics:
        图像范围: ±√(levels×λR)
        亮度转换: B = (I/4) × 255
        其中 I 是光强 [0, 4]，B 是亮度 [0, 255]

    Implementation Notes:
        - 使用 numpy.meshgrid 创建规则网格
        - 使用 numpy 广播机制高效计算
        - 返回值可直接用于 matplotlib 的 imshow 或转为 PIL 图像

    Examples:
        # 生成标准牛顿环图像数据
        >>> X, Y, B, ym = newtons_rings_2d(589.3e-9, 1.0, levels=50)
        >>> import matplotlib.pyplot as plt
        >>> plt.imshow(B, extent=[-ym, ym, -ym, ym])
        >>> plt.colorbar(label='Intensity')
    """
    # 确定计算范围
    ym = np.sqrt(levels * lam * R)

    # 创建二维网格
    xs = np.linspace(-ym, ym, resolution)
    ys = np.linspace(-ym, ym, resolution)
    X, Y = np.meshgrid(xs, ys)

    # 计算径向距离（到中心的距离）
    r = np.sqrt(X**2 + Y**2)

    # 计算光程差
    d = compute_optical_path_difference(r, R, curvature_diff, h)

    # 计算光强分布
    I = compute_intensity(d, lam, n)

    # 转换为亮度值 [0, 255]
    B = (I / 4.0) * 255

    return X, Y, B, ym