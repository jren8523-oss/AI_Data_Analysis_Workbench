# -*- coding: utf-8 -*-
"""抽样估计（任务 05）：大样本总体均值 / 总体比例区间估计。

课程口径：随机抽取 n=100 户居民，95% 置信水平，z = 1.96（大样本 n≥30）。
全部为确定性计算，每个结果带 公式→代入→结果→解释 四件套。
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from . import fmt

Z_95 = 1.96  # 课程指定 95% 置信水平下的 z 值


def _four(value, formula, substitution, interpretation, nd=2) -> dict:
    return {
        "value": float(value),
        "value_s": fmt.num(value, nd),
        "formula": formula,
        "substitution": substitution,
        "interpretation": interpretation,
    }


def mean_interval(x: pd.Series, conf: float = 0.95, z: float = Z_95) -> dict:
    """大样本总体均值区间估计：x̄ ± z·(s/√n)。

    返回：
    {
      n, mean, std(样本标准差, ddof=1), se, z, margin,
      lower, upper, large_sample: bool, 各字段四件套…
    }
    """
    s = x.dropna().astype(float)
    n = int(len(s))
    mean = float(s.mean())
    std = float(s.std(ddof=1))
    se = std / math.sqrt(n)
    margin = z * se
    lower = mean - margin
    upper = mean + margin
    large_sample = n >= 30

    return {
        "n": n,
        "large_sample": large_sample,
        "mean": _four(mean, "x̄ = Σx / n",
                      f"x̄ = {fmt.num(s.sum(), 2)} / {n}",
                      f"样本均值 x̄ = {fmt.num(mean)} 元，是总体均值 μ 的点估计。"),
        "std": _four(std, "s = √[Σ(x − x̄)² / (n − 1)]",
                     f"（样本标准差，n={n}）",
                     f"样本标准差 s = {fmt.num(std)} 元，反映样本数据的离散程度。"),
        "se": _four(se, "SE = s / √n",
                    f"SE = {fmt.num(std)} / √{n}",
                    f"抽样标准误 SE = {fmt.num(se)} 元，表示样本均值估计总体均值的平均误差。"),
        "z": _four(z, "z（95% 置信水平）",
                   f"查标准正态分布表，P(|Z|≤1.96)=0.95",
                   f"置信水平 {fmt.pct(conf, 0)} 对应 z = {z}。"),
        "margin": _four(margin, "E = z · SE",
                        f"E = {z} × {fmt.num(se, 4)}",
                        f"允许误差 E = {fmt.num(margin)} 元。"),
        "lower": lower, "upper": upper,
        "interval": _four((lower + upper) / 2,
                          "置信区间 = x̄ ± E",
                          f"[{fmt.num(mean)} − {fmt.num(margin)}, {fmt.num(mean)} + {fmt.num(margin)}]",
                          f"在 {fmt.pct(conf, 0)} 置信水平下，总体月电费均值的置信区间为 "
                          f"[{fmt.num(lower)} 元, {fmt.num(upper)} 元]。"),
    }


def proportion_interval(p_hat: float, n: int, conf: float = 0.95, z: float = Z_95) -> dict:
    """大样本总体比例区间估计：p̂ ± z·√(p̂(1−p̂)/n)。"""
    se = math.sqrt(p_hat * (1 - p_hat) / n)
    margin = z * se
    lower = max(0.0, p_hat - margin)
    upper = min(1.0, p_hat + margin)

    return {
        "p_hat": _four(p_hat, "p̂ = 具备特征的单位数 / n",
                       f"p̂ = {fmt.num(p_hat * n, 0)} / {n}",
                       f"样本比例 p̂ = {fmt.pct(p_hat)}，即样本中月电费高于 80 元的户数占比。"),
        "se": _four(se, "SE = √[p̂(1−p̂)/n]",
                    f"SE = √[{fmt.pct(p_hat)} × {fmt.pct(1 - p_hat)} / {n}]",
                    f"比例抽样标准误 SE = {fmt.pct(se, 2)}。"),
        "margin": _four(margin, "E = z · SE",
                        f"E = {z} × {fmt.num(se, 4)}",
                        f"允许误差 E = {fmt.pct(margin, 2)}。"),
        "lower": lower, "upper": upper,
        "interval": _four((lower + upper) / 2,
                          "置信区间 = p̂ ± E",
                          f"[{fmt.pct(p_hat)} − {fmt.pct(margin, 2)}, {fmt.pct(p_hat)} + {fmt.pct(margin, 2)}]",
                          f"在 {fmt.pct(conf, 0)} 置信水平下，总体中月电费高于 80 元居民比例的置信区间为 "
                          f"[{fmt.pct(lower, 1)}, {fmt.pct(upper, 1)}]。"),
    }


def required_sample_size(std: float, margin: float, z: float = Z_95) -> int:
    """按精度反推所需样本量 n = (z·s/E)²，向上取整。"""
    return int(math.ceil((z * std / margin) ** 2))
