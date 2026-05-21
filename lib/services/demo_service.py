# -*- coding: utf-8 -*-
"""Demo calculation services for Newton rings endpoints."""

from lib.config import get_wavelength_cmap, init_matplotlib_fonts
from lib.physics import newtons_rings_1d, newtons_rings_2d
from lib.plotting import create_intensity_plot, create_ring_image


init_matplotlib_fonts()


def _render_demo_result(
    *,
    wavelength_nm,
    reference_radius_m,
    refractive_n,
    title,
    plot_title,
    spacing_nm=0,
    curvature_diff=0.0,
):
    lam = wavelength_nm * 1e-9
    h = spacing_nm * 1e-9

    r, intensity, _ = newtons_rings_1d(
        lam=lam,
        R=reference_radius_m,
        n=refractive_n,
        h=h,
        curvature_diff=curvature_diff,
    )
    X, Y, brightness, _ = newtons_rings_2d(
        lam=lam,
        R=reference_radius_m,
        n=refractive_n,
        h=h,
        curvature_diff=curvature_diff,
        levels=50,
    )

    ring_image = create_ring_image(
        X,
        Y,
        brightness,
        wavelength_nm,
        title,
        get_wavelength_cmap,
    )
    intensity_plot = create_intensity_plot(
        r,
        intensity,
        wavelength_nm,
        reference_radius_m,
        plot_title,
    )

    return {
        "success": True,
        "ring_image": f"data:image/png;base64,{ring_image}",
        "intensity_plot": f"data:image/png;base64,{intensity_plot}",
    }


def calculate_normal_newton_rings(wavelength_nm, radius_m, spacing_nm, refractive_n):
    try:
        return _render_demo_result(
            wavelength_nm=wavelength_nm,
            reference_radius_m=radius_m,
            refractive_n=refractive_n,
            spacing_nm=spacing_nm,
            title=f"牛顿环模拟图像（λ={wavelength_nm:.1f}nm, h={spacing_nm:.0f}nm）",
            plot_title=f"光强分布曲线（λ={wavelength_nm:.1f}nm, R={radius_m:.2f}m）",
        )
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def calculate_truncated_newton_rings(wavelength_nm, radius_m, height_nm, refractive_n):
    return calculate_normal_newton_rings(wavelength_nm, radius_m, height_nm, refractive_n)


def calculate_convex_concave_contact(wavelength_nm, R1_m, R2_m, refractive_n):
    try:
        curvature_diff = 1 / R1_m - 1 / R2_m
        return _render_demo_result(
            wavelength_nm=wavelength_nm,
            reference_radius_m=R1_m,
            refractive_n=refractive_n,
            curvature_diff=curvature_diff,
            title=f"平凸-平凹透镜（接触式）\nλ={wavelength_nm:.1f}nm, R1={R1_m:.2f}m, R2={R2_m:.2f}m",
            plot_title=f"曲率差异分析（R1/R2={R1_m / R2_m:.2f}）",
        )
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def calculate_convex_convex_contact(wavelength_nm, R1_m, R2_m, refractive_n):
    try:
        curvature_diff = 1 / R1_m + 1 / R2_m
        return _render_demo_result(
            wavelength_nm=wavelength_nm,
            reference_radius_m=R1_m,
            refractive_n=refractive_n,
            curvature_diff=curvature_diff,
            title=f"双平凸透镜（接触式）\nλ={wavelength_nm:.1f}nm, R1={R1_m:.2f}m, R2={R2_m:.2f}m",
            plot_title=f"双凸面干涉分析（R1={R1_m:.2f}m, R2={R2_m:.2f}m）",
        )
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def calculate_convex_concave_noncontact(wavelength_nm, R1_m, R2_m, spacing_nm, refractive_n):
    try:
        curvature_diff = 1 / R1_m - 1 / R2_m
        return _render_demo_result(
            wavelength_nm=wavelength_nm,
            reference_radius_m=R1_m,
            refractive_n=refractive_n,
            spacing_nm=spacing_nm,
            curvature_diff=curvature_diff,
            title=f"平凸-平凹透镜（非接触式）\nλ={wavelength_nm:.1f}nm, h={spacing_nm:.0f}nm",
            plot_title=f"间距影响分析（h={spacing_nm:.0f}nm）",
        )
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def calculate_convex_convex_noncontact(wavelength_nm, R1_m, R2_m, spacing_nm, refractive_n):
    try:
        curvature_diff = 1 / R1_m + 1 / R2_m
        return _render_demo_result(
            wavelength_nm=wavelength_nm,
            reference_radius_m=R1_m,
            refractive_n=refractive_n,
            spacing_nm=spacing_nm,
            curvature_diff=curvature_diff,
            title=f"双平凸透镜（非接触式）\nλ={wavelength_nm:.1f}nm, h={spacing_nm:.0f}nm",
            plot_title=f"双凸面非接触干涉分析（h={spacing_nm:.0f}nm）",
        )
    except Exception as exc:
        return {"success": False, "error": str(exc)}
