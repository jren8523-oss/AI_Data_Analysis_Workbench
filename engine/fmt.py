# -*- coding: utf-8 -*-
"""数字格式化：千分位、百分比、精度控制，消除浮点脏值（如 0.30000000000000004）。"""
from __future__ import annotations


def clean(x, tol: float = 1e-9) -> float:
    """把接近整数的浮点脏值清理为整数。"""
    if x is None:
        return float("nan")
    try:
        f = float(x)
    except (TypeError, ValueError):
        return float("nan")
    if f != f:  # NaN
        return f
    r = round(f)
    if abs(f - r) < tol:
        return float(r)
    return f


def num(x, nd: int = 2, thousand: bool = True) -> str:
    """普通数字，千分位 + 保留 nd 位小数（自动去尾零）。"""
    f = clean(x)
    if f != f:
        return "—"
    if abs(f - round(f)) < 1e-9:
        s = f"{int(round(f)):,}" if thousand else str(int(round(f)))
        return s
    s = f"{f:,.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def pct(x, nd: int = 1, thousand: bool = False) -> str:
    """百分比（x 本身是小数，如 0.2345 -> 23.5%）。"""
    f = clean(x)
    if f != f:
        return "—"
    s = f"{f * 100:,.{nd}f}" if thousand else f"{f * 100:.{nd}f}"
    return s + "%"


def sign(x, nd: int = 2) -> str:
    """带正负号的数字（用于增长量等）。"""
    f = clean(x)
    if f != f:
        return "—"
    if f > 0:
        return "+" + num(f, nd)
    return num(f, nd)


def sign_pct(x, nd: int = 1) -> str:
    """带正负号的百分比。"""
    f = clean(x)
    if f != f:
        return "—"
    s = f"{abs(f * 100):.{nd}f}%"
    return ("+" + s) if f >= 0 else ("-" + s)
