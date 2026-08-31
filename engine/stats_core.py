# -*- coding: utf-8 -*-
"""描述性统计核心：集中趋势、离散程度、分布形态。

每个指标返回 {value, formula, substitution, interpretation} 四件套，
供报告直接渲染（公式 + 代入 + 结果 + 解释），也供 QA 复核取值。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import fmt


def _four(value, formula: str, substitution: str, interpretation: str, nd: int = 2) -> dict:
    return {
        "value": float(value),
        "value_s": fmt.num(value, nd),
        "formula": formula,
        "substitution": substitution,
        "interpretation": interpretation,
    }


def central_tendency(x: pd.Series) -> dict:
    """集中趋势：均值 / 中位数 / 众数（取最小众数，与 Excel MODE 一致）。"""
    s = x.dropna()
    n = len(s)
    mean = s.mean()
    median = s.median()
    mode_series = s.mode()
    mode = float(mode_series.min()) if len(mode_series) else float("nan")

    return {
        "n": n,
        "mean": _four(mean, "x̄ = Σx / n",
                      f"x̄ = {fmt.num(s.sum(), 2)} / {n}",
                      f"平均值为 {fmt.num(mean)}，表示数据的「重心」所在。"),
        "median": _four(median, "M = 排序后居中的值",
                        f"n={n}，取第 {(n+1)//2} 位数值",
                        f"中位数为 {fmt.num(median)}，表示有一半数据低于该值，不受极端值影响。"),
        "mode": _four(mode, "众数 = 出现次数最多的值",
                      f"最高频取值为 {mode_series.iloc[0] if len(mode_series) else '—'}（出现 {int((s == mode_series.min()).sum())} 次）",
                      f"众数为 {fmt.num(mode)}，是数据中出现最频繁的值（取最小众数，与 Excel MODE 一致）。"),
        "mean_gt_median": bool(mean > median),
    }


def dispersion(x: pd.Series) -> dict:
    """离散程度：极差/平均差/方差/标准差/四分位差/变异系数。"""
    s = x.dropna()
    n = len(s)
    rng = s.max() - s.min()
    mad = (s - s.mean()).abs().mean()
    var = s.var(ddof=1)          # 样本方差（教材默认无偏）
    std = s.std(ddof=1)
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    cv = std / s.mean() if s.mean() != 0 else float("nan")

    return {
        "range": _four(rng, "R = max − min",
                       f"R = {fmt.num(s.max())} − {fmt.num(s.min())}",
                       f"极差为 {fmt.num(rng)}，反映数据整体的波动跨度。"),
        "mad": _four(mad, "A.D. = Σ|x − x̄| / n",
                     f"A.D. = {fmt.num((s - s.mean()).abs().sum(), 2)} / {n}",
                     f"平均差为 {fmt.num(mad)}，表示各数据偏离平均值的平均幅度。"),
        "var": _four(var, "s² = Σ(x − x̄)² / (n − 1)",
                     f"s² = {fmt.num(((s - s.mean())**2).sum(), 2)} / {n - 1}",
                     f"样本方差为 {fmt.num(var)}，是离散程度的平方度量（无偏估计）。"),
        "std": _four(std, "s = √s²",
                     f"s = √{fmt.num(var, 4)}",
                     f"标准差为 {fmt.num(std)}，与数据同量纲，是最常用的离散程度指标。"),
        "iqr": _four(iqr, "IQR = Q3 − Q1",
                     f"IQR = {fmt.num(q3)} − {fmt.num(q1)}",
                     f"四分位差为 {fmt.num(iqr)}，反映中间 50% 数据的离散程度，抗极端值。"),
        "cv": _four(cv, "CV = s / x̄",
                    f"CV = {fmt.num(std)} / {fmt.num(s.mean())}",
                    f"变异系数为 {fmt.pct(cv, 2)}，无量纲，可跨组比较离散程度。", nd=4),
    }


def distribution_shape(x: pd.Series) -> dict:
    """分布形态：偏度 / 峰度（基于 scipy，无 scipy 时退化为 pandas 实现）。"""
    s = x.dropna()
    n = len(s)
    try:
        from scipy import stats
        skew = float(stats.skew(s, bias=False))
        kurt = float(stats.kurtosis(s, bias=False))   # 超额峰度，正态=0
        skew_impl, kurt_impl = "scipy", "scipy"
    except ImportError:
        skew = _skew_pandas(s)
        kurt = _kurt_pandas(s)
        skew_impl, kurt_impl = "pandas", "pandas"

    if skew > 0.5:
        skew_desc = "右偏（正偏），右侧有长尾，均值通常大于中位数。"
    elif skew < -0.5:
        skew_desc = "左偏（负偏），左侧有长尾，均值通常小于中位数。"
    else:
        skew_desc = "近似对称分布。"
    if kurt > 1:
        kurt_desc = "尖峰分布，数据比正态更集中于均值附近，且尾部更厚。"
    elif kurt < -1:
        kurt_desc = "平峰分布，数据比正态更分散。"
    else:
        kurt_desc = "峰度接近正态分布水平。"

    return {
        "skew": _four(skew, "偏度 SK = Σ(x − x̄)³ / (n·s³)",
                      f"（样本偏度，n={n}）", skew_desc, nd=3),
        "kurt": _four(kurt, "峰度 K = Σ(x − x̄)⁴ / (n·s⁴) − 3",
                      f"（样本超额峰度，正态分布为 0）", kurt_desc, nd=3),
        "skew_impl": skew_impl,
        "kurt_impl": kurt_impl,
    }


def _skew_pandas(s: pd.Series) -> float:
    n = len(s)
    if n < 3:
        return float("nan")
    m = s.mean()
    m2 = ((s - m) ** 2).sum() / n
    m3 = ((s - m) ** 3).sum() / n
    if m2 == 0:
        return float("nan")
    return float(m3 / (m2 ** 1.5))


def _kurt_pandas(s: pd.Series) -> float:
    n = len(s)
    if n < 4:
        return float("nan")
    m = s.mean()
    m2 = ((s - m) ** 2).sum() / n
    m4 = ((s - m) ** 4).sum() / n
    if m2 == 0:
        return float("nan")
    return float(m4 / (m2 ** 2) - 3)


def full_descriptive(x: pd.Series) -> dict:
    """一次算全：集中趋势 + 离散程度 + 分布形态。"""
    return {
        "central": central_tendency(x),
        "dispersion": dispersion(x),
        "shape": distribution_shape(x),
    }
