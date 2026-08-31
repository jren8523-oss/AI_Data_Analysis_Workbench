# -*- coding: utf-8 -*-
"""生成 9 份示例数据 CSV（task01~task10 除 02）到 data/raw/。

全部使用固定随机种子（可复现），按课程文字描述构造：
- 任务 05：100 户电费，约 30–40% 户 > 80 元（生成后校验并微调）
- 任务 07：研发投入 x（3~20 万元）与销售额 y，保证 R² > 0.8、预测点 x=15 在样本内
- 任务 08：2010–2024 年总产值，上行趋势
其余按 v2.2 §五 规格构造。
生成后打印各文件行数与关键校验，供 QA 对照。
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(20240831)


def save(df: pd.DataFrame, name: str) -> None:
    path = RAW / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  {name}.csv  {df.shape[0]} 行 × {df.shape[1]} 列 -> {path.name}")


# ---------------- task01 店铺访客数（12 个月 × 5 类目） ----------------
def make_task01():
    months = [f"{m}月" for m in range(1, 13)]
    # 各来源基线 + 全年趋势 + 季节波动（6月/11月小高峰）
    base = {"直接访问": 1500, "搜索引擎": 2200, "社交媒体": 1200, "外部链接": 800, "广告投放": 900}
    trend = np.linspace(0, 2600, 12)
    season = np.array([0, 80, 150, 120, 180, 420, 260, 300, 220, 350, 680, 520])
    rows = {}
    for src, b in base.items():
        noise = rng.normal(0, 90, 12)
        rows[src] = np.maximum(0, b + trend * (0.75 if src in ("直接访问", "搜索引擎") else 1.0)
                               + season * (0.4 if src == "广告投放" else 1.0) + noise).round(0).astype(int)
    df = pd.DataFrame({"月份": months})
    for src in base:
        df[src] = rows[src]
    df["总访客数"] = df[[c for c in base]].sum(axis=1)
    save(df, "task01")


# ---------------- task03 数据清洗与加工（60 行脏数据） ----------------
def make_task03():
    industries = ["制造业", "零售业", "批发业", "餐饮业", "建筑业"]
    base_sales = {"制造业": 3200, "零售业": 2800, "批发业": 2400, "餐饮业": 1800, "建筑业": 4200}
    records = []
    for ind in industries:
        for m in range(1, 13):
            sales = base_sales[ind] + rng.normal(0, 260) + m * 18
            records.append({"行业": ind, "月份": m, "日期": f"2024-{m:02d}-15",
                            "销售额": round(sales, 1)})
    df = pd.DataFrame(records)
    # 注入脏数据（约 10 处，覆盖 缺失/文本型/错误日期/异常值/重复行/脏名称）
    dirty = [
        # (行索引, 字段, 脏值)
        (3, "销售额", "1,250.5"),        # 文本型数字（千分位逗号）
        (8, "销售额", "¥3200"),          # 文本型数字（货币符号）
        (15, "销售额", None),            # 缺失
        (22, "销售额", None),            # 缺失
        (27, "销售额", 99999),           # 异常值（明显偏离）
        (31, "销售额", -800),            # 异常值（负数）
        (40, "日期", "2024-2-30"),       # 错误日期（2月无30日）
        (44, "日期", "2024/13/01"),      # 错误日期（13月）
        (6, "行业", " 制造业"),           # 脏名称（前导空格）
        (19, "行业", "零售业 "),          # 脏名称（尾随空格）
        (29, "行业", "批发 业"),          # 脏名称（中间空格）
        (35, "行业", "餐饮业"),           # 与 36 行构成重复
        (36, "行业", "餐饮业"),           # 重复行（同行其他字段也相同）
    ]
    for idx, col, val in dirty:
        df.loc[idx, col] = val
    # 确保 35/36 两行完全重复：把 36 行的月份/日期/销售额也改成与 35 一致
    df.loc[36, ["月份", "日期", "销售额"]] = df.loc[35, ["月份", "日期", "销售额"]]
    save(df, "task03")


# ---------------- task04 生产资料市场价格（1–5 月 × 4 品种） ----------------
def make_task04():
    varieties = ["螺纹钢", "线材", "中厚板", "热轧卷板"]
    base_price = {"螺纹钢": 4050, "线材": 4200, "中厚板": 4500, "热轧卷板": 4300}
    df = pd.DataFrame({"月份": [f"{m}月" for m in range(1, 6)]})
    for v in varieties:
        drift = np.linspace(0, rng.uniform(150, 380), 5)
        wave = np.array([0, -60, 90, -40, 120]) * rng.uniform(0.5, 1.0)
        df[v] = (base_price[v] + drift + wave + rng.normal(0, 18, 5)).round(0).astype(int)
    save(df, "task04")


# ---------------- task05 小区居民用电（100 户电费，30–40% > 80 元） ----------------
def make_task05():
    while True:
        # 混合分布：70% 低用电(20~90) + 30% 高用电(80~260)，右偏
        n_low = 70
        low = rng.uniform(22, 92, n_low)
        high = rng.uniform(82, 270, 30)
        x = np.concatenate([low, high])
        rng.shuffle(x)
        p_gt80 = float((x > 80).mean())
        if 0.30 <= p_gt80 <= 0.40 and 55 <= x.mean() <= 85:
            break
    df = pd.DataFrame({"户号": [f"户{i+1:03d}" for i in range(100)], "月电费(元)": x.round(1)})
    save(df, "task05")
    print(f"    -> 校验: >80元占比 {p_gt80:.1%}, 均值 {x.mean():.1f} 元")


# ---------------- task06 产品总成本变动（3 种产品） ----------------
def make_task06():
    df = pd.DataFrame({
        "产品": ["产品A", "产品B", "产品C"],
        "产量q0(件)": [2000, 1500, 1800],
        "产量q1(件)": [2400, 1600, 2000],
        "单位成本p0(元)": [12.0, 8.0, 15.0],
        "单位成本p1(元)": [10.0, 9.0, 14.0],
    })
    save(df, "task06")


# ---------------- task07 研发与销售（20 次抽样，R² > 0.8） ----------------
def make_task07():
    while True:
        x = rng.uniform(3, 20, 20).round(1)
        y = 42 + 17.5 * x + rng.normal(0, 14, 20)
        # 保证 R²>0.8 且 15 在样本范围内
        corr = np.corrcoef(x, y)[0, 1]
        if corr ** 2 > 0.85 and 15 >= x.min() and 15 <= x.max():
            break
    df = pd.DataFrame({"样本编号": [f"样本{i+1:02d}" for i in range(20)],
                       "研发投入x(万元)": x, "销售额y(万元)": y.round(1)})
    save(df, "task07")
    print(f"    -> 校验: R²={corr**2:.3f}, x范围[{x.min()}, {x.max()}], 含15: {bool((x.min()<=15<=x.max()))}")


# ---------------- task08 企业总产值（2010–2024，上行趋势） ----------------
def make_task08():
    years = list(range(2010, 2025))
    t = np.arange(15)
    base = np.array([3.2, 3.6, 3.9, 4.3, 4.8, 5.4, 6.0, 6.7, 7.5, 8.2, 9.1, 10.0, 10.9, 11.8, 12.8])
    noise = np.array([0, -0.15, 0.1, -0.2, 0.15, 0.1, -0.1, 0.2, -0.15, 0.25, -0.2, 0.15, 0.1, -0.25, 0.2])
    df = pd.DataFrame({"年份": years, "总产值(亿元)": (base + noise).round(2)})
    save(df, "task08")


# ---------------- task09 网店访客数（7 天 × 6 类目长表） ----------------
def make_task09():
    cats = ["服装", "数码", "家居", "食品", "美妆", "图书"]
    base = {"服装": 2600, "数码": 2100, "家居": 1600, "食品": 1300, "美妆": 900, "图书": 600}
    days = pd.date_range("2024-01-01", periods=7, freq="D")
    rows = []
    for day in days:
        dow = day.weekday()
        wf = 1.0 + (0.35 if dow >= 5 else 0.0)   # 周末上浮
        for cat in cats:
            v = base[cat] * wf + rng.normal(0, 90)
            rows.append({"日期": day.strftime("%Y-%m-%d"), "商品类目": cat,
                         "访客数": int(max(0, v))})
    df = pd.DataFrame(rows)
    save(df, "task09")


# ---------------- task10 销售数据分析报告（3 年 × 12 月 × 3 办事处） ----------------
def make_task10():
    offices = ["华东办事处", "华南办事处", "华北办事处"]
    off_base = {"华东办事处": 620, "华南办事处": 470, "华北办事处": 350}
    year_scale = {2022: 1.00, 2023: 1.18, 2024: 1.38}
    season = np.array([0.85, 0.9, 1.0, 1.05, 1.1, 1.15, 1.08, 1.12, 1.25, 1.3, 1.45, 1.55])
    rows = []
    for yr in [2022, 2023, 2024]:
        for m in range(1, 13):
            for off in offices:
                v = off_base[off] * year_scale[yr] * season[m - 1] + rng.normal(0, 35)
                rows.append({"年份": yr, "月份": m, "办事处": off,
                             "销售额(万元)": round(max(0, v), 1)})
    df = pd.DataFrame(rows)
    save(df, "task10")


if __name__ == "__main__":
    print("生成示例数据（固定随机种子 20240831，可复现）:")
    make_task01()
    make_task03()
    make_task04()
    make_task05()
    make_task06()
    make_task07()
    make_task08()
    make_task09()
    make_task10()
    print("全部完成 ->", RAW)
