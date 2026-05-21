# -*- coding: utf-8 -*-
"""Data analysis services for Newton rings measurements."""

import csv

import numpy as np

from lib.plotting import create_fit_plot, create_ring_image_by_R


def process_data(csv_content, wavelength_nm, refractive_n):
    try:
        lines = csv_content.strip().split("\n")
        if len(lines) < 3:
            return {"success": False, "error": "CSV文件至少需要3行数据"}

        rows = list(csv.reader(lines))
        if len(rows) < 3:
            return {"success": False, "error": "CSV文件至少需要3行数据"}

        k = []
        left_positions = []
        right_positions = []

        for val in rows[0][1:]:
            try:
                if val.strip():
                    k.append(int(float(val.strip())))
            except ValueError:
                continue

        for val in rows[1][1:]:
            try:
                if val.strip():
                    left_positions.append(float(val.strip()))
            except ValueError:
                continue

        for val in rows[2][1:]:
            try:
                if val.strip():
                    right_positions.append(float(val.strip()))
            except ValueError:
                continue

        min_length = min(len(k), len(left_positions), len(right_positions))
        if min_length < 3:
            return {"success": False, "error": "有效数据点太少，至少需要3个数据点"}

        k = np.array(k[:min_length])
        left_positions = np.array(left_positions[:min_length])
        right_positions = np.array(right_positions[:min_length])

        diameter_mm = np.abs(left_positions - right_positions)
        diameter_sq = (diameter_mm * 1e-3) ** 2
        X = np.column_stack([k, np.ones_like(k)])
        coefficients, _, _, _ = np.linalg.lstsq(X, diameter_sq, rcond=None)

        fit_plot, calculated_R = create_fit_plot(
            k,
            diameter_sq,
            coefficients,
            wavelength_nm,
            refractive_n,
        )
        ring_image = create_ring_image_by_R(calculated_R, wavelength_nm, refractive_n)

        return {
            "success": True,
            "calculated_R": round(calculated_R, 2),
            "fit_plot": f"data:image/png;base64,{fit_plot}",
            "ring_image": f"data:image/png;base64,{ring_image}",
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}
