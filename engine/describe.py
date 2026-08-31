# -*- coding: utf-8 -*-
"""Describe：数据概况（规模/字段/类型/缺失/唯一值/分布/异常/示例）。

遵循工作台原则「先理解数据，再分析」——任何任务开始前先生成数据概况。
"""
from __future__ import annotations

import pandas as pd

from . import fmt


def describe(df: pd.DataFrame, sample_rows: int = 5) -> dict:
    """生成结构化的数据概况字典。

    返回结构（供报告渲染与 QA 共用）：
    {
      "n_rows": int, "n_cols": int,
      "columns": [ {name, dtype, missing, missing_pct, nunique, sample} ],
      "numeric_summary": {col: {mean, min, max, ...}} | None,
      "head": [[...], ...], "head_cols": [...],
      "issues": [ "发现：xxx" ... ]   # 自动发现的值得注意的点
    }
    """
    n_rows, n_cols = df.shape
    cols = []
    issues = []

    for c in df.columns:
        s = df[c]
        miss = int(s.isna().sum())
        nunique = int(s.nunique(dropna=True))
        col_info = {
            "name": str(c),
            "dtype": _dtype_label(s),
            "missing": miss,
            "missing_pct": miss / n_rows if n_rows else 0.0,
            "nunique": nunique,
            "sample": _sample(s),
        }
        if pd.api.types.is_numeric_dtype(s):
            col_info["min"] = fmt.num(s.min(), 2)
            col_info["max"] = fmt.num(s.max(), 2)
            col_info["mean"] = fmt.num(s.mean(), 2)
        cols.append(col_info)

        # 自动发现问题
        if miss > 0:
            issues.append(f"字段「{c}」存在 {miss} 个缺失值（{fmt.pct(miss / n_rows)}）")
        if pd.api.types.is_numeric_dtype(s) and nunique <= 2:
            issues.append(f"字段「{c}」仅有 {nunique} 个取值（近常量字段）")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    numeric_summary = None
    if numeric_cols:
        d = df[numeric_cols].describe().T
        numeric_summary = {
            col: {
                "count": int(d.loc[col, "count"]),
                "mean": fmt.num(d.loc[col, "mean"], 2),
                "std": fmt.num(d.loc[col, "std"], 2),
                "min": fmt.num(d.loc[col, "min"], 2),
                "q25": fmt.num(d.loc[col, "25%"], 2),
                "q50": fmt.num(d.loc[col, "50%"], 2),
                "q75": fmt.num(d.loc[col, "75%"], 2),
                "max": fmt.num(d.loc[col, "max"], 2),
            }
            for col in numeric_cols
        }

    head = df.head(sample_rows).fillna("").astype(str).values.tolist()

    return {
        "n_rows": int(n_rows),
        "n_cols": int(n_cols),
        "columns": cols,
        "numeric_summary": numeric_summary,
        "head": head,
        "head_cols": [str(c) for c in df.columns],
        "issues": issues,
    }


def _dtype_label(s: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(s):
        return "数值"
    if pd.api.types.is_datetime64_any_dtype(s):
        return "日期"
    return "文本"


def _sample(s: pd.Series, k: int = 3) -> str:
    vals = [str(v) for v in s.dropna().unique()[:k]]
    if not vals:
        return "—"
    if len(vals) > 1:
        return "、".join(vals[:2]) + " …"
    return vals[0]
