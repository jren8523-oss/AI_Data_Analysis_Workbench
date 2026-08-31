# -*- coding: utf-8 -*-
"""matplotlib 图表工厂：中文字体、16:9、PNG 输出。

所有图表函数返回 (png相对路径, 图表说明dict)，PNG 写入 output/taskNN/charts/。
图表与正文同源取数：调用方传入计算好的指标 dict，本模块只负责画，不重算。
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd

from . import config, fmt

# ---------- 中文字体 ----------
_FONT_LOADED = False


def _load_font():
    global _FONT_LOADED
    if _FONT_LOADED:
        return
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",       # 微软雅黑
        "C:/Windows/Fonts/msyh.ttf",
        "C:/Windows/Fonts/simhei.ttf",     # 黑体
        "C:/Windows/Fonts/simsun.ttc",     # 宋体
    ]
    picked = None
    for c in candidates:
        p = Path(c)
        if p.exists():
            picked = str(p)
            break
    if picked:
        try:
            fm.fontManager.addfont(picked)
            name = fm.FontProperties(fname=picked).get_name()
            plt.rcParams["font.family"] = [name, "sans-serif"]
            plt.rcParams["axes.unicode_minus"] = False
            _FONT_LOADED = True
            return name
        except Exception:
            pass
    plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False
    _FONT_LOADED = True
    return "Microsoft YaHei"


def _setup_ax(ax):
    ax.set_facecolor("white")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#C9D4DE")
    ax.spines["bottom"].set_color("#C9D4DE")
    ax.tick_params(colors="#4A5568")
    ax.yaxis.grid(True, color="#EEF2F6", linewidth=0.8)
    ax.set_axisbelow(True)


def _title_ax(ax, title, subtitle=None):
    ax.set_title(title, fontsize=16, fontweight="bold", color=config.BRAND_DARK, pad=14)
    if subtitle:
        ax.text(0.5, 1.02, subtitle, transform=ax.transAxes, ha="center",
                fontsize=10.5, color=config.GRAY, va="bottom")


def _save(fig, out_dir: Path, name: str) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.png"
    fig.savefig(path, dpi=config.DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return f"charts/{name}.png"


def bar(df: pd.DataFrame, x: str, y: str, out_dir: Path, name: str,
        title: str, subtitle: str = "", color: str = config.BRAND,
        value_labels: bool = True, sort: bool = False, ylabel: str = ""):
    """柱形图。df 已按展示顺序排列；sort=True 时按 y 降序。"""
    _load_font()
    d = df.sort_values(y, ascending=False) if sort else df
    fig, ax = plt.subplots(figsize=config.FIG_SIZE, dpi=config.DPI)
    bars = ax.bar(d[x].astype(str), d[y], color=color, width=0.62, zorder=3)
    if value_labels:
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                    fmt.num(b.get_height(), 0),
                    ha="center", va="bottom", fontsize=10.5, color="#2D3748")
    _setup_ax(ax)
    _title_ax(ax, title, subtitle)
    ax.set_ylabel(ylabel or y, fontsize=11.5, color="#4A5568")
    ax.set_ylim(0, max(d[y]) * 1.15 if len(d) else 1)
    fig.tight_layout()
    return _save(fig, out_dir, name)


def line(df: pd.DataFrame, x: str, ys: list, out_dir: Path, name: str,
         title: str, subtitle: str = "", markers: bool = True,
         legend_loc: str = "upper left", ylabel: str = "",
         colors: list | None = None, annotate_last: tuple | None = None):
    """折线图，支持多系列。annotate_last=(y_col, text) 标注最后一个点。"""
    _load_font()
    fig, ax = plt.subplots(figsize=config.FIG_SIZE, dpi=config.DPI)
    cols = colors or [config.BRAND, config.ACCENT, "#3E8E7E", "#8E5FA2", "#C05621"]
    xs = np.arange(len(df))
    for i, ycol in enumerate(ys):
        c = cols[i % len(cols)]
        ax.plot(xs, df[ycol], color=c, linewidth=2.6, marker="o" if markers else None,
                markersize=5.5, label=ycol, zorder=3)
        if annotate_last and annotate_last[0] == ycol:
            last_x, last_y = xs[-1], df[ycol].iloc[-1]
            ax.annotate(annotate_last[1], xy=(last_x, last_y), xytext=(8, 10),
                        textcoords="offset points", fontsize=10.5, color=config.BRAND_DARK,
                        fontweight="bold")
    _setup_ax(ax)
    _title_ax(ax, title, subtitle)
    ax.set_xticks(xs)
    ax.set_xticklabels([str(v) for v in df[x]], rotation=0, fontsize=10.5)
    ax.set_ylabel(ylabel or ys[0], fontsize=11.5, color="#4A5568")
    ax.legend(loc=legend_loc, frameon=False, fontsize=10.5)
    fig.tight_layout()
    return _save(fig, out_dir, name)


def pie(df: pd.DataFrame, label_col: str, value_col: str, out_dir: Path, name: str,
        title: str, subtitle: str = "", show_pct: bool = True):
    """饼图。df 已按占比排序，前 N 项外归并为「其他」。"""
    _load_font()
    MAX_SLICE = 6
    d = df.sort_values(value_col, ascending=False).copy()
    if len(d) > MAX_SLICE:
        top = d.head(MAX_SLICE - 1)
        other_val = d.iloc[MAX_SLICE - 1:][value_col].sum()
        other = pd.DataFrame([{label_col: "其他", value_col: other_val}])
        d = pd.concat([top, other], ignore_index=True)
    labels = d[label_col].astype(str)
    vals = d[value_col].astype(float)
    total = vals.sum() or 1.0
    fig, ax = plt.subplots(figsize=config.FIG_SIZE, dpi=config.DPI)
    colors = ["#005DA2", "#3E8E7E", "#F2A900", "#8E5FA2", "#C05621", "#5B7C99"]
    wedges, texts, autotexts = ax.pie(
        vals, labels=labels, autopct=(lambda p: f"{p:.1f}%") if show_pct else None,
        colors=colors[:len(vals)], startangle=90, counterclock=False,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"fontsize": 11, "color": "#2D3748"},
        pctdistance=0.72,
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_color("white")
        at.set_fontweight("bold")
    _title_ax(ax, title, subtitle)
    ax.text(0, 0.02, f"合计 {fmt.num(total, 0)}", ha="center", fontsize=12,
            color=config.BRAND_DARK, fontweight="bold")
    fig.tight_layout()
    return _save(fig, out_dir, name)


def scatter_reg(x: np.ndarray, y: np.ndarray, out_dir: Path, name: str,
                title: str, subtitle: str, xlabel: str, ylabel: str,
                a: float = None, b: float = None,
                pred_x: float = None, pred_y: float = None):
    """散点图 + 回归线 + 预测点。a/b 为回归截距/斜率（y = a + bx）。"""
    _load_font()
    fig, ax = plt.subplots(figsize=config.FIG_SIZE, dpi=config.DPI)
    ax.scatter(x, y, s=70, color=config.BRAND, alpha=0.85, zorder=3, label="样本数据点")
    if a is not None and b is not None:
        xs = np.linspace(min(x) * 0.9, max(x) * 1.15, 100)
        ax.plot(xs, a + b * xs, color=config.ACCENT, linewidth=2.4, zorder=2,
                label=f"回归线 ŷ = {fmt.num(a)} + {fmt.num(b)}·x")
    if pred_x is not None and pred_y is not None:
        ax.scatter([pred_x], [pred_y], s=140, marker="*", color="#C0392B",
                   zorder=4, label=f"预测点（x={fmt.num(pred_x, 1)} → ŷ={fmt.num(pred_y, 1)}）")
        ax.axvline(pred_x, color="#C0392B", linestyle="--", linewidth=1, alpha=0.4)
    _setup_ax(ax)
    _title_ax(ax, title, subtitle)
    ax.set_xlabel(xlabel, fontsize=11.5, color="#4A5568")
    ax.set_ylabel(ylabel, fontsize=11.5, color="#4A5568")
    ax.legend(frameon=False, fontsize=10.5)
    fig.tight_layout()
    return _save(fig, out_dir, name)


def hist_box(x: np.ndarray, out_dir: Path, name_prefix: str, title_h: str, title_b: str,
             bins: int = 8, xlabel: str = "", mean_val: float = None,
             ci_lower: float = None, ci_upper: float = None):
    """直方图（可叠加均值线与置信区间）+ 箱线图，两子图一页。"""
    _load_font()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=config.FIG_SIZE, dpi=config.DPI,
                                   gridspec_kw={"width_ratios": [3, 2]})
    n, bins_e, patches = ax1.hist(x, bins=bins, color=config.BRAND, edgecolor="white",
                                  alpha=0.9, zorder=3)
    if mean_val is not None:
        ax1.axvline(mean_val, color=config.ACCENT, linewidth=2.2, linestyle="--",
                    label=f"均值 x̄={fmt.num(mean_val)}")
    if ci_lower is not None and ci_upper is not None:
        ax1.axvspan(ci_lower, ci_upper, color=config.ACCENT, alpha=0.15,
                    label=f"95% 置信区间 [{fmt.num(ci_lower)}, {fmt.num(ci_upper)}]")
    ax1.legend(frameon=False, fontsize=9.5, loc="upper right")
    _setup_ax(ax1)
    ax1.set_title(title_h, fontsize=14, fontweight="bold", color=config.BRAND_DARK)
    ax1.set_xlabel(xlabel, fontsize=11, color="#4A5568")
    ax1.set_ylabel("频数", fontsize=11, color="#4A5568")

    bp = ax2.boxplot(x, vert=True, patch_artist=True, widths=0.5)
    bp["boxes"][0].set_facecolor(config.BRAND_LIGHT)
    bp["boxes"][0].set_edgecolor(config.BRAND)
    for key in ("whiskers", "caps", "medians"):
        for e in bp[key]:
            e.set_color(config.BRAND)
            e.set_linewidth(1.8)
    _setup_ax(ax2)
    ax2.set_title(title_b, fontsize=14, fontweight="bold", color=config.BRAND_DARK)
    ax2.set_xticks([])
    fig.tight_layout()
    return _save(fig, out_dir, f"{name_prefix}_hist_box")


def ts_forecast(years, values, trend_vals, out_dir: Path, name: str,
                title: str, subtitle: str, forecast_year=None, forecast_val=None,
                trend_label="线性趋势拟合", ylabel="总产值（亿元）"):
    """时间序列图：实际值折线 + 趋势拟合线 + 外推预测点（红星）。"""
    _load_font()
    ys = [str(y) for y in years]
    xs = np.arange(len(values))
    fig, ax = plt.subplots(figsize=config.FIG_SIZE, dpi=config.DPI)
    ax.plot(xs, values, color=config.BRAND, linewidth=2.8, marker="o", markersize=6,
            label="实际总产值", zorder=3)
    ax.plot(xs, trend_vals, color=config.ACCENT, linewidth=2.2, linestyle="--",
            label=trend_label, zorder=2)
    if forecast_year is not None and forecast_val is not None:
        fx = np.arange(len(values) + 1)
        ax.scatter([fx[-1]], [forecast_val], s=150, marker="*", color="#C0392B",
                   zorder=4, label=f"预测 {forecast_year} 年")
        ax.axvline(fx[-2], color="#C0392B", linestyle=":", linewidth=1, alpha=0.5)
        ax.annotate(f"{fmt.num(forecast_val, 1)}", xy=(fx[-1], forecast_val),
                    xytext=(-12, -26), textcoords="offset points",
                    fontsize=11, color="#C0392B", fontweight="bold", ha="center")
        ax.set_xticks(np.arange(len(values) + 1))
        ax.set_xticklabels(ys + [str(forecast_year)], fontsize=10, rotation=0)
    else:
        ax.set_xticks(xs)
        ax.set_xticklabels(ys, fontsize=10)
    _setup_ax(ax)
    _title_ax(ax, title, subtitle)
    ax.set_ylabel(ylabel, fontsize=11.5, color="#4A5568")
    ax.legend(frameon=False, fontsize=10.5, loc="upper left")
    fig.tight_layout()
    return _save(fig, out_dir, name)


def grouped_bar(df: pd.DataFrame, x: str, y_cols: list, out_dir: Path, name: str,
                title: str, subtitle: str = "", labels: list | None = None,
                ylabel: str = "", value_labels: bool = True):
    """分组柱形图（多个系列的并列柱）。"""
    _load_font()
    fig, ax = plt.subplots(figsize=config.FIG_SIZE, dpi=config.DPI)
    xs = np.arange(len(df))
    width = 0.8 / len(y_cols)
    colors = ["#005DA2", "#F2A900", "#3E8E7E", "#8E5FA2"]
    for i, ycol in enumerate(y_cols):
        c = colors[i % len(colors)]
        bars = ax.bar(xs + (i - (len(y_cols) - 1) / 2) * width, df[ycol],
                      width=width * 0.92, color=c, label=(labels or y_cols)[i], zorder=3)
        if value_labels:
            for b in bars:
                ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                        fmt.num(b.get_height(), 1), ha="center", va="bottom",
                        fontsize=8.6, color="#2D3748")
    _setup_ax(ax)
    _title_ax(ax, title, subtitle)
    ax.set_xticks(xs)
    ax.set_xticklabels([str(v) for v in df[x]], fontsize=10.5)
    ax.set_ylabel(ylabel, fontsize=11.5, color="#4A5568")
    ax.legend(frameon=False, fontsize=10, loc="upper left", ncol=len(y_cols))
    ymax = max(df[c].max() for c in y_cols)
    ax.set_ylim(0, ymax * 1.18 if ymax else 1)
    fig.tight_layout()
    return _save(fig, out_dir, name)


def grouped_line(df: pd.DataFrame, x: str, y_cols: list, out_dir: Path, name: str,
                 title: str, subtitle: str = "", labels: list | None = None,
                 ylabel: str = "", legend_loc: str = "upper left"):
    """多系列折线图（年度比较等）。"""
    _load_font()
    fig, ax = plt.subplots(figsize=config.FIG_SIZE, dpi=config.DPI)
    xs = np.arange(len(df))
    colors = ["#005DA2", "#F2A900", "#3E8E7E"]
    for i, ycol in enumerate(y_cols):
        c = colors[i % len(colors)]
        ax.plot(xs, df[ycol], color=c, linewidth=2.6, marker="o", markersize=6,
                label=(labels or y_cols)[i], zorder=3)
    _setup_ax(ax)
    _title_ax(ax, title, subtitle)
    ax.set_xticks(xs)
    ax.set_xticklabels([str(v) for v in df[x]], fontsize=10.5)
    ax.set_ylabel(ylabel, fontsize=11.5, color="#4A5568")
    ax.legend(frameon=False, fontsize=10.5, loc=legend_loc, ncol=len(y_cols))
    fig.tight_layout()
    return _save(fig, out_dir, name)
