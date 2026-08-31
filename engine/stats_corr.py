# -*- coding: utf-8 -*-
"""相关与回归分析（任务 07）：相关系数、一元线性回归、拟合优度、预测。

课程口径（人邮社《统计与数据分析基础》）：
- 相关系数 r = Σ(x−x̄)(y−ȳ) / √[Σ(x−x̄)²·Σ(y−ȳ)²]，−1 ≤ r ≤ 1
- 相关程度分级：|r|<0.3 弱相关；0.3≤|r|<0.5 低度相关；0.5≤|r|<0.8 显著(中度)相关；|r|≥0.8 高度相关
- 一元线性回归（最小二乘）：ŷ = a + bx，b = Σ(x−x̄)(y−ȳ)/Σ(x−x̄)²，a = ȳ − b·x̄
- 拟合优度 R² = r²（一元回归）
- 重要：相关关系 ≠ 因果关系（报告必须警示）
"""
from __future__ import annotations

import math

import numpy as np

from . import fmt


def correlation(x, y) -> dict:
    """皮尔逊相关系数 + 方向 + 程度分级。"""
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    n = len(xa)
    xm, ym = xa.mean(), ya.mean()
    cov = ((xa - xm) * (ya - ym)).sum()
    sx = math.sqrt(((xa - xm) ** 2).sum())
    sy = math.sqrt(((ya - ym) ** 2).sum())
    r = float(cov / (sx * sy)) if sx * sy else float("nan")

    if abs(r) >= 0.8:
        degree = "高度相关"
    elif abs(r) >= 0.5:
        degree = "显著相关（中度）"
    elif abs(r) >= 0.3:
        degree = "低度相关"
    else:
        degree = "弱相关（基本不相关）"
    direction = "正相关" if r > 0 else ("负相关" if r < 0 else "零相关")

    return {
        "n": n,
        "r": r,
        "r_s": fmt.num(r, 4),
        "direction": direction,
        "degree": degree,
        "formula": "r = Σ(x−x̄)(y−ȳ) / √[Σ(x−x̄)²·Σ(y−ȳ)²]",
        "substitution": (f"x̄={fmt.num(xm)}, ȳ={fmt.num(ym)}，"
                         f"Σ(x−x̄)(y−ȳ)={fmt.num(cov, 2)}，"
                         f"√[Σ(x−x̄)²·Σ(y−ȳ)²]={fmt.num(sx * sy, 2)}"),
        "interpretation": (f"r = {fmt.num(r, 4)}：{direction}，{degree}。"
                           f"说明研发投入与销售额之间存在{('正的线性关系' if r > 0 else '负的线性关系')}。"
                           f"注意：这仅表明统计上的线性关联，不能直接推断因果关系。"),
    }


def linreg(x, y) -> dict:
    """一元线性回归最小二乘：ŷ = a + bx。"""
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    n = len(xa)
    xm, ym = xa.mean(), ya.mean()
    sxx = ((xa - xm) ** 2).sum()
    sxy = ((xa - xm) * (ya - ym)).sum()
    b = float(sxy / sxx) if sxx else float("nan")
    a = float(ym - b * xm)

    yhat = a + b * xa
    sst = ((ya - ym) ** 2).sum()
    sse = ((ya - yhat) ** 2).sum()
    r2 = float(1 - sse / sst) if sst else float("nan")

    return {
        "n": n, "a": a, "b": b,
        "a_s": fmt.num(a, 4), "b_s": fmt.num(b, 4),
        "r2": r2, "r2_s": fmt.pct(r2, 1),
        "equation": f"ŷ = {fmt.num(a, 4)} + {fmt.num(b, 4)}·x",
        "b_formula": "b = Σ(x−x̄)(y−ȳ) / Σ(x−x̄)²",
        "b_substitution": f"Σ(x−x̄)(y−ȳ)={fmt.num(sxy, 2)}，Σ(x−x̄)²={fmt.num(sxx, 2)}",
        "b_interpretation": f"斜率 b = {fmt.num(b, 4)}：研发投入每增加 1 万元，销售额平均增加 {fmt.num(b, 2)} 万元。",
        "a_formula": "a = ȳ − b·x̄",
        "a_substitution": f"a = {fmt.num(ym)} − {fmt.num(b, 4)}×{fmt.num(xm)}",
        "a_interpretation": f"截距 a = {fmt.num(a, 2)}：当研发投入为 0 时的销售额基准水平（仅数学含义）。",
        "r2_interpretation": f"决定系数 R² = {fmt.pct(r2, 1)}：研发投入可以解释销售额变动的 {fmt.pct(r2, 1)}，拟合效果好。",
    }


def predict(model: dict, x0: float) -> dict:
    """预测：ŷ₀ = a + b·x₀。"""
    y0 = model["a"] + model["b"] * x0
    return {
        "x0": x0, "y0": y0,
        "y0_s": fmt.num(y0, 2),
        "formula": "ŷ₀ = a + b·x₀",
        "substitution": f"ŷ = {model['a_s']} + {model['b_s']}×{fmt.num(x0)}",
        "interpretation": f"当研发投入为 {fmt.num(x0)} 万元时，预测销售额约为 {fmt.num(y0, 2)} 万元。"
                          f"（预测点位于样本数据范围内，属于内插预测，可靠性较高）",
    }
