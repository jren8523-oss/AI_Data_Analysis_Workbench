# -*- coding: utf-8 -*-
"""时间序列分析（任务 08）：发展水平、增长量、发展速度、增长速度、趋势方程、预测。

课程口径（人邮社《统计与数据分析基础》，按年度序列）：
- 平均发展水平（序时平均）ȳ = Σy / n
- 平均增长量 = (y_n − y_1) / (n − 1)
- 环比发展速度 = y_i / y_{i−1}（%）；定基发展速度 = y_i / y_1（%）
- 环比增长速度 = 环比发展速度 − 100%；定基增长速度 = 定基发展速度 − 100%
- 平均发展速度（几何平均法）＝ (y_n / y_1)^(1/(n−1))
- 平均增长速度 = 平均发展速度 − 100%
- 线性趋势方程 ŷ = a + bt（最小二乘，t 取 0,1,…,n−1）
- 外推预测 2025 年（注意外推适用范围警示）
"""
from __future__ import annotations

import math

import numpy as np

from . import fmt


def growth_analysis(years: list, values: list) -> dict:
    """发展水平与增长量分析。"""
    y = np.asarray(values, dtype=float)
    n = len(y)
    avg_level = float(y.mean())
    avg_growth = float((y[-1] - y[0]) / (n - 1))
    total_growth = float(y[-1] - y[0])

    # 环比 / 定基发展速度与增长速度
    ratios = [None] + [float(y[i] / y[i - 1]) for i in range(1, n)]          # 环比发展速度
    base_ratios = [1.0] + [float(y[i] / y[0]) for i in range(1, n)]          # 定基发展速度
    mom_growth = [None] + [r - 1 for r in ratios[1:]]                        # 环比增长速度
    base_growth = [0.0] + [r - 1 for r in base_ratios[1:]]                   # 定基增长速度

    # 平均发展速度（几何平均）、平均增长速度
    avg_ratio = float((y[-1] / y[0]) ** (1 / (n - 1)))
    avg_growth_rate = avg_ratio - 1

    return {
        "years": list(years), "values": [float(v) for v in y],
        "n": n,
        "avg_level": avg_level,
        "total_growth": total_growth,
        "avg_growth": avg_growth,
        "ratios": ratios, "base_ratios": base_ratios,
        "mom_growth": mom_growth, "base_growth": base_growth,
        "avg_ratio": avg_ratio, "avg_growth_rate": avg_growth_rate,
    }


def trend_equation(years: list, values: list) -> dict:
    """线性趋势方程 ŷ = a + bt（最小二乘，t=0,1,…,n−1）。"""
    y = np.asarray(values, dtype=float)
    n = len(y)
    t = np.arange(n)
    tm, ym = t.mean(), y.mean()
    stt = ((t - tm) ** 2).sum()
    sty = ((t - tm) * (y - ym)).sum()
    b = float(sty / stt) if stt else float("nan")
    a = float(ym - b * tm)

    yhat = a + b * t
    sst = ((y - ym) ** 2).sum()
    sse = ((y - yhat) ** 2).sum()
    r2 = float(1 - sse / sst) if sst else float("nan")

    return {
        "a": a, "b": b,
        "a_s": fmt.num(a, 4), "b_s": fmt.num(b, 4),
        "r2": r2, "r2_s": fmt.pct(r2, 1),
        "equation": f"ŷ = {fmt.num(a, 4)} + {fmt.num(b, 4)}·t（t = 0,1,…,{n-1}）",
        "b_interpretation": f"斜率 b = {fmt.num(b, 2)}：总产值平均每年增加约 {fmt.num(b, 2)} 亿元。",
        "a_interpretation": f"截距 a = {fmt.num(a, 2)} 亿元：当 t=0（第 1 年）时的趋势值。",
        "r2_interpretation": f"趋势拟合 R² = {fmt.pct(r2, 1)}，线性趋势对总产值的解释程度很高。",
    }


def forecast(trend: dict, target_year: int, base_year: int) -> dict:
    """按趋势方程外推预测：t = target_year − base_year（t 从 0 开始）。"""
    t = target_year - base_year
    yhat = trend["a"] + trend["b"] * t
    return {
        "target_year": target_year, "t": t, "yhat": yhat,
        "yhat_s": fmt.num(yhat, 2),
        "formula": "ŷ = a + b·t",
        "substitution": f"ŷ = {trend['a_s']} + {trend['b_s']}×{t}",
        "interpretation": f"预测 {target_year} 年企业总产值约为 {fmt.num(yhat, 2)} 亿元。"
                          f"（此预测基于趋势外推，前提是影响总产值的因素保持稳定）",
    }


def format_speed_table(ga: dict) -> list:
    """发展速度表行：[年份, 总产值, 增长量, 环比发展速度%, 环比增长速度%, 定基发展速度%, 定基增长速度%]"""
    rows = []
    prev = None
    for i, yr in enumerate(ga["years"]):
        v = ga["values"][i]
        growth = v - prev if prev is not None else "—"
        row = [str(yr), fmt.num(v, 2), fmt.num(growth, 2) if prev is not None else "—",
               "—" if i == 0 else fmt.pct(ga["ratios"][i], 1),
               "—" if i == 0 else fmt.pct(ga["mom_growth"][i], 1),
               "100.0%" if i == 0 else fmt.pct(ga["base_ratios"][i], 1),
               "—" if i == 0 else fmt.pct(ga["base_growth"][i], 1)]
        rows.append(row)
        prev = v
    return rows
