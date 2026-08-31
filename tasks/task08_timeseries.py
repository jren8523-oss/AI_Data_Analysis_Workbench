# -*- coding: utf-8 -*-
"""任务 08 · 分析并预测企业总产值：时间序列分析（发展水平/速度/趋势方程/预测）。

课程口径：15 年总产值，计算平均发展水平、平均增长量、环比/定基发展速度与增长速度、
平均发展速度（几何平均）、平均增长速度、线性趋势方程，预测 2025 年总产值。
必须提示外推预测适用范围。
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from engine import config, fmt, io_utils, report, stats_ts, viz
from engine import qa as qa_mod
from tasks import _common as C

TASK_NO = 8
TARGET_YEAR = 2025


def build(out_dir: Path) -> qa_mod.QA:
    qa = qa_mod.QA()
    hash_before = io_utils.raw_hash("task08")
    df = io_utils.read_csv("task08")
    years = df["年份"].astype(int).tolist()
    values = df["总产值(亿元)"].astype(float).tolist()

    ga = stats_ts.growth_analysis(years, values)
    trend = stats_ts.trend_equation(years, values)
    fc = stats_ts.forecast(trend, TARGET_YEAR, base_year=years[0])
    trend_vals = [trend["a"] + trend["b"] * t for t in range(ga["n"])]

    # ---------- 图表 ----------
    ts_png = viz.ts_forecast(years, values, trend_vals, out_dir / "charts", "08_ts",
                             "企业总产值：实际值 + 趋势线 + 2025 预测",
                             f"线性趋势方程 {trend['equation']}（R²={trend['r2_s']}）",
                             forecast_year=TARGET_YEAR, forecast_val=float(fc["yhat"]))

    # ---------- 区块 ----------
    blocks = [
        C.need_block(
            "这家企业 2010–2024 年的总产值是如何发展的？按此趋势，2025 年总产值预计是多少？",
            "15 年（2010–2024）企业总产值（亿元），示例数据为上行趋势",
            "计算平均发展水平/平均增长量/环比与定基发展速度/增长速度/平均发展速度/平均增长速度，"
            "建立线性趋势方程并预测 2025 年，同时说明外推适用范围"),
        C.desc_block(df, [("年份跨度", "15", "2010~2024"), ("预测目标", "2025 年", "趋势外推")]),
        report.block("③ I 挖掘数据 · 指标计算（水平 → 速度 → 趋势 → 预测）", "".join([
            report.metric_grid([
                ("平均发展水平", fmt.num(ga["avg_level"], 2), "亿元（序时平均）"),
                ("累计增长量", fmt.sign(ga["total_growth"], 2), "亿元（期末−期初）"),
                ("平均增长量", fmt.sign(ga["avg_growth"], 2), "亿元/年"),
                ("平均发展速度", fmt.pct(ga["avg_ratio"], 1), "几何平均"),
                ("平均增长速度", fmt.pct(ga["avg_growth_rate"], 1), "平均发展速度 − 100%"),
            ]),
            report.step_card(1, "发展水平与增长量",
                             "平均发展水平 ȳ = Σy/n；平均增长量 = (yₙ − y₁)/(n−1)。"),
            report.formula_box("平均发展水平", "ȳ = Σy / n",
                               f"ȳ = {fmt.num(sum(values), 2)} / {ga['n']}",
                               fmt.num(ga["avg_level"], 2),
                               f"15 年总产值的序时平均水平为 {fmt.num(ga['avg_level'], 2)} 亿元。"),
            report.formula_box("平均增长量", "(yₙ − y₁) / (n − 1)",
                               f"({fmt.num(values[-1], 2)} − {fmt.num(values[0], 2)}) / 14",
                               fmt.sign(ga["avg_growth"], 2),
                               f"平均每年增长 {fmt.num(ga['avg_growth'], 2)} 亿元。"),
            report.step_card(2, "发展速度与增长速度",
                             "环比发展速度 = yᵢ/yᵢ₋₁；定基发展速度 = yᵢ/y₁；增长速度 = 发展速度 − 100%。"),
            report.table(["年份", "总产值(亿元)", "增长量", "环比发展速度", "环比增长速度", "定基发展速度", "定基增长速度"],
                         stats_ts.format_speed_table(ga),
                         caption="表：发展水平与速度指标（2010–2024）", small=True),
            report.formula_box("平均发展速度（几何平均）", "x̄ = (yₙ / y₁)^(1/(n−1))",
                               f"x̄ = ({fmt.num(values[-1], 2)} / {fmt.num(values[0], 2)})^(1/14)",
                               fmt.pct(ga["avg_ratio"], 1),
                               f"年平均发展速度 {fmt.pct(ga['avg_ratio'], 1)}，"
                               f"平均增长速度 {fmt.pct(ga['avg_growth_rate'], 1)}。"),
            report.step_card(3, "线性趋势方程（最小二乘）",
                             "ŷ = a + bt，t = 0,1,…,14；b = Σ(t−t̄)(y−ȳ)/Σ(t−t̄)²，a = ȳ − b·t̄。"),
            report.formula_box("趋势方程", "ŷ = a + bt",
                               "（t = 0,1,…,14，对应 2010–2024）", trend["equation"],
                               f"{trend['b_interpretation']} {trend['r2_interpretation']}"),
            report.step_card(4, "外推预测 · 2025 年", "把 t = 15 代入趋势方程。"),
            report.formula_box("预测 2025 年总产值", fc["formula"], fc["substitution"],
                               fc["yhat_s"], fc["interpretation"]),
            report.warn("外推预测适用范围：趋势方程基于 2010–2024 年数据拟合，预测的前提是「影响总产值的因素在未来保持相对稳定」。"
                        "若出现政策调整、市场剧变、重大技术变革等结构性变化，外推预测可能失效——预测值只能作为参考，不可作为确定事实。"),
        ]), id="dig"),
        report.block("④ 图表 · 趋势与预测",
                     report.figure(ts_png, "图1 总产值趋势与 2025 年预测",
                                   "图表目的：直观展示上升趋势与预测外推点",
                                   f"核心发现：总产值稳步上升，按趋势方程预测 {TARGET_YEAR} 年约 {fc['yhat_s']} 亿元")),
        C.g_block(
            "时间序列分析回答「过去怎么发展、未来怎么走」：先看水平与速度，再拟合趋势，最后外推预测。",
            f"15 年平均总产值 {fmt.num(ga['avg_level'], 2)} 亿元，平均每年增长 {fmt.num(ga['avg_growth'], 2)} 亿元；"
            f"平均发展速度 {fmt.pct(ga['avg_ratio'], 1)}。",
            f"若趋势延续，{TARGET_YEAR} 年总产值预计 {fc['yhat_s']} 亿元，可用于年度目标设定与资源规划。",
            [
                ("事实", f"总产值从 {fmt.num(values[0], 2)} 亿元（2010）增至 {fmt.num(values[-1], 2)} 亿元（2024），累计增长 {fmt.num(ga['total_growth'], 2)} 亿元。"),
                ("分析", f"线性趋势拟合 R² = {trend['r2_s']}，总产值基本沿直线上升，年增约 {fmt.num(trend['b'], 2)} 亿元。"),
                ("推测", "持续增长可能与行业扩张/产能释放有关；2025 预测 {fc['yhat_s']} 亿元基于趋势延续假设。"),
                ("建议", "以预测值为基准做年度目标，同时预留 10% 上下的弹性空间，以应对环境变化。"),
            ]),
        C.prompt_block(
            "这是某企业 2010–2024 年总产值数据（CSV：年份、总产值(亿元)）。请："
            "1) 计算平均发展水平、平均增长量、环比/定基发展速度、环比/定基增长速度、平均发展速度（几何平均）、平均增长速度；"
            "2) 用最小二乘法建立线性趋势方程 ŷ = a + bt；3) 预测 2025 年总产值；4) 必须说明外推预测的适用条件与局限。",
            "学生验收要点：平均发展速度 = (期末/期初)^(1/14)；预测 = a + b×15（t 从 0 起）；外推警示必须出现。"),
        C.qa_block(qa),
    ]

    report.render(TASK_NO, blocks, out_dir / "report.html", qa.results,
                  bottom_note=report.bottom_note(
                      "时序四步：看水平 → 算速度 → 拟趋势 → 外推预测——预测永远带假设，结论永远留余地。"))

    # ---------- QA ----------
    qa.check("样本量 n = 15", ga["n"] == 15, f"实际 {ga['n']} 年")
    qa.check("年份连续", all(years[i + 1] - years[i] == 1 for i in range(len(years) - 1)),
             f"{years[0]}~{years[-1]} 逐年连续")
    qa.check("趋势方向与数据一致（上行）", values[-1] > values[0] and trend["b"] > 0,
             f"期末 > 期初，斜率 b = {fmt.num(trend['b'], 3)} > 0")
    qa.check("平均增长量复算（手写路径）",
             qa.approx(ga["avg_growth"], (values[-1] - values[0]) / (len(values) - 1)),
             "平均增长量 = (期末−期初)/(n−1)")
    qa.check("平均发展速度复算（几何平均）",
             qa.approx(ga["avg_ratio"], (values[-1] / values[0]) ** (1 / (len(values) - 1))),
             f"x̄ = (期末/期初)^(1/14) = {fmt.pct(ga['avg_ratio'], 2)}")
    qa.check("预测值复算（手写路径）",
             qa.approx(fc["yhat"], trend["a"] + trend["b"] * (TARGET_YEAR - years[0])),
             f"t = {TARGET_YEAR - years[0]} 代入方程")
    qa.check("外推预警必现", "外推" in (out_dir / "report.html").read_text(encoding="utf-8"),
             "外推预测适用范围说明已渲染")
    qa.check("原始数据未被修改", io_utils.raw_hash("task08") == hash_before, "SHA-256 一致")
    qa.check("图表已生成且非空",
             all(p.stat().st_size > 0 for p in (out_dir / "charts").glob("*.png")),
             "PNG 非空")
    return qa
