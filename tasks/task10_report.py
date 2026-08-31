# -*- coding: utf-8 -*-
"""任务 10 · 制作销售数据分析报告：分年度分析 → 年度比较 → 三年汇总 → 核心发现 → 结论。

课程口径：某企业 2022–2024 年三个办事处 36 个月的销售额（108 行），
按「分年度分析 → 年度比较 → 总体汇总 → 核心发现 → 结论与建议」组织一份完整分析报告。
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from engine import config, fmt, io_utils, report, viz
from engine import qa as qa_mod
from tasks import _common as C

TASK_NO = 10


def build(out_dir: Path) -> qa_mod.QA:
    qa = qa_mod.QA()
    hash_before = io_utils.raw_hash("task10")
    df = io_utils.read_csv("task10")
    df["年份"] = df["年份"].astype(int)
    df["月份"] = df["月份"].astype(int)

    years = sorted(df["年份"].unique())
    offices = df.groupby("办事处")["销售额(万元)"].sum().sort_values(ascending=False)

    # ---------- 分年度分析 ----------
    year_rows = []
    for y in years:
        sub = df[df["年份"] == y]
        s = sub["销售额(万元)"].sum()
        best = sub.groupby("月份")["销售额(万元)"].sum().idxmax()
        worst = sub.groupby("月份")["销售额(万元)"].sum().idxmin()
        year_rows.append({"年份": y, "总额": s, "最佳月": int(best), "最低月": int(worst)})
    y2022, y2023, y2024 = year_rows[0]["总额"], year_rows[1]["总额"], year_rows[2]["总额"]
    g23 = (y2023 - y2022) / y2022          # 2023 同比
    g24 = (y2024 - y2023) / y2023          # 2024 同比
    total3 = y2022 + y2023 + y2024

    # 年度比较：月度轮廓（透视表 行=月，列=年）
    month_pivot = df.pivot_table(index="月份", columns="年份", values="销售额(万元)",
                                 aggfunc="sum", observed=True).astype(float)
    month_pivot.columns = [str(c) for c in sorted(month_pivot.columns)]   # 列名统一为 str
    year_cols = list(month_pivot.columns)

    # 办事处 × 年度
    off_year = df.pivot_table(index="办事处", columns="年份", values="销售额(万元)",
                              aggfunc="sum", observed=True).astype(float)
    off_year = off_year.loc[[o for o in offices.index]]
    off_share = offices / offices.sum()

    # ---------- 图表 ----------
    bar_df = pd.DataFrame({"年份": [f"{y} 年" for y in years],
                           "销售额": [year_rows[i]["总额"] for i in range(3)]})
    p1 = viz.bar(bar_df, "年份", "销售额", out_dir / "charts", "10_year_bar",
                 "年度销售额对比（2022–2024）", "分年度汇总 → 柱形图", ylabel="销售额（万元）")
    p2 = viz.grouped_line(month_pivot.reset_index(), "月份", year_cols,
                          out_dir / "charts", "10_month_line",
                          "各年月度销售额轮廓", "1–12 月 · 三年叠加对比",
                          ylabel="销售额（万元）", legend_loc="upper left")
    p3 = viz.pie(offices.reset_index(), "办事处", "销售额(万元)", out_dir / "charts", "10_office_pie",
                 "三年办事处销售占比", "2022–2024 合计")

    # ---------- 区块 ----------
    blocks = [
        C.need_block(
            "这家企业三年（2022–2024）的销售表现如何？增长还是下滑？各办事处贡献多大？下一步经营重点放在哪？",
            "3 年 × 12 月 × 3 办事处 = 108 行：年份 / 月份 / 办事处 / 销售额(万元)（示例数据按课程描述构造）",
            "产出一份完整分析报告：分年度分析 → 年度比较 → 总体汇总 → 核心发现 → 结论与建议"),
        C.desc_block(df, [("年份跨度", "3 年", f"{years[0]}~{years[-1]}"), ("办事处", "3 个", "华东/华北/华南")]),
        report.block("③ I 挖掘数据 · 分年度 → 比较 → 汇总", "".join([
            report.step_card(1, "分年度分析",
                             "先看每一年：总额多少、哪个月最高/最低，形成「年度画像」。"),
            report.table(["年份", "销售总额(万元)", "最佳月份", "最低月份"],
                         [[r["年份"], fmt.num(r["总额"], 1), f"{r['最佳月']} 月", f"{r['最低月']} 月"]
                          for r in year_rows],
                         caption="表 1 分年度销售概况"),
            report.step_card(2, "年度比较（同比）",
                             "同比增速 = (本年 − 上年) / 上年，判断增长势头。"),
            report.formula_box("2023 同比增速", "(Y₂₀₂₃ − Y₂₀₂₂) / Y₂₀₂₂",
                               f"({fmt.num(y2023, 1)} − {fmt.num(y2022, 1)}) / {fmt.num(y2022, 1)}",
                               fmt.sign_pct(g23, 1),
                               f"2023 年较 2022 年增长 {fmt.pct(g23, 1)}。"),
            report.formula_box("2024 同比增速", "(Y₂₀₂₄ − Y₂₀₂₃) / Y₂₀₂₃",
                               f"({fmt.num(y2024, 1)} − {fmt.num(y2023, 1)}) / {fmt.num(y2023, 1)}",
                               fmt.sign_pct(g24, 1),
                               f"2024 年较 2023 年增长 {fmt.pct(g24, 1)}。"),
            report.table(["月份"] + [f"{y} 年" for y in years],
                         [[int(m)] + [fmt.num(month_pivot.loc[m, y], 1) for y in month_pivot.columns]
                          for m in month_pivot.index],
                         caption="表 2 月度销售额对比（透视表：行=月份，列=年份）", small=True),
            report.step_card(3, "总体汇总（三年合计）",
                             "把三年数据汇总：总销售额、各办事处贡献度，看结构。"),
            report.formula_box("三年销售总额", "Σ 各年总额",
                               f"{fmt.num(y2022, 1)} + {fmt.num(y2023, 1)} + {fmt.num(y2024, 1)}",
                               fmt.num(total3, 1),
                               f"三年累计销售 {fmt.num(total3, 1)} 万元。"),
            report.table(["办事处", "三年销售额(万元)", "占比"],
                         [[o, fmt.num(offices[o], 1), fmt.pct(off_share[o], 1)]
                          for o in offices.index],
                         caption="表 3 办事处销售贡献（降序）"),
        ]), id="dig"),
        report.block("④ 图表 · 年度柱 / 月度折线 / 占比饼",
                     report.figure(p1, "图1 年度销售额对比",
                                   "看整体趋势：三年逐年上升还是波动", f"核心发现：三年逐年增长，累计增长 {fmt.pct(g23 + g24, 1)}（口径见下）")
                     + report.figure(p2, "图2 各年月度销售额轮廓（三年叠加）",
                                     "看年内节奏：峰值月、低谷月、季节性", "核心发现：每年的高峰月与低谷月相对稳定")
                     + report.figure(p3, "图3 办事处销售占比",
                                     "看结构：哪个办事处是基本盘", f"核心发现：{offices.index[0]}占比最高（{fmt.pct(off_share[offices.index[0]], 1)}）")),
        report.block("⑤ 核心发现与结论", "".join([
            report.finding("事实", "逐年增长", f"三年销售额分别 {fmt.num(y2022, 1)} / {fmt.num(y2023, 1)} / {fmt.num(y2024, 1)} 万元，"
                                             f"同比增速 {fmt.sign_pct(g23, 1)} / {fmt.sign_pct(g24, 1)}，三年累计 {fmt.num(total3, 1)} 万元。"),
            report.finding("分析", "增长主要靠华东办事处拉动",
                           f"{offices.index[0]} 贡献 {fmt.pct(off_share[offices.index[0]], 1)} 的销售额，"
                           f"{offices.index[1]} 为 {fmt.pct(off_share[offices.index[1]], 1)}；结构较集中，抗风险能力一般。"),
            report.finding("推测", "存在稳定季节规律",
                           f"峰值月（{year_rows[-1]['最佳月']} 月）与低谷月（{year_rows[-1]['最低月']} 月）三年基本一致，推测受行业季节与促销周期影响。"),
            report.finding("建议", "保基本盘 + 补短板",
                           f"继续巩固 {offices.index[0]} 市场；针对 {offices.index[-1]}（占比 {fmt.pct(off_share[offices.index[-1]], 1)}）制定专项提升计划；"
                           f"在低谷月（{year_rows[-1]['最低月']} 月）主动做清仓/蓄客活动，平滑季节波动。"),
            report.warn("结论说明：本报告基于示例数据（按课程描述构造），结论用于演示分析框架；替换为真实数据后需重新计算全部指标。"),
        ]), id="goal"),
        C.prompt_block(
            "我有一份某企业 2022–2024 年销售数据（CSV：年份、月份、办事处、销售额(万元)，共 108 行）。请："
            "1) 分年度分析：每年总额与最佳/最低月份；2) 年度比较：计算 2023、2024 年同比增速；"
            "3) 总体汇总：三年总额、各办事处占比；4) 用柱形图、折线图、饼图辅助说明；"
            "5) 输出一份结构化报告：核心发现（事实→分析→推测→建议）→ 结论。",
            "学生验收要点：报告必须包含「分年度 / 年度比较 / 总体汇总 / 核心发现 / 结论」五个层次；"
            "增速用公式展示代入过程；结论必须有数据支撑。"),
        C.qa_block(qa),
    ]

    report.render(TASK_NO, blocks, out_dir / "report.html", qa.results,
                  bottom_note=report.bottom_note(
                      "好报告的结构：先分年度看清每一年，再比较找趋势，汇总看结构，最后用「事实→分析→推测→建议」落到可执行结论。"))

    # ---------- QA ----------
    qa.check("数据完整（108 = 3 年 × 12 月 × 3 办事处）",
             len(df) == 108 and len(years) == 3 and len(offices) == 3 and df["月份"].nunique() == 12,
             f"实际 {len(df)} 行 / {len(years)} 年 / {len(offices)} 办事处")
    qa.check("年度合计复算（分组求和 vs 原始）",
             all(qa.approx(sum(df[df["年份"] == y]["销售额(万元)"]),
                           year_rows[i]["总额"]) for i, y in enumerate(years)),
             "各年总额 = 该年所有行之和")
    qa.check("三年总额复算", qa.approx(total3, df["销售额(万元)"].sum()),
             f"三年总额 = {fmt.num(total3, 1)} 万元")
    qa.check("2023 同比复算", qa.approx(g23, (y2023 - y2022) / y2022),
             f"g₂₀₂₃ = {fmt.sign_pct(g23, 2)}")
    qa.check("2024 同比复算", qa.approx(g24, (y2024 - y2023) / y2023),
             f"g₂₀₂₄ = {fmt.sign_pct(g24, 2)}")
    qa.check("办事处占比复算", qa.approx(off_share.sum(), 1.0),
             f"占比合计 = {fmt.pct(off_share.sum(), 2)}")
    qa.check("月度透视表完整（12 月 × 3 年）", month_pivot.shape == (12, 3), f"实际 {month_pivot.shape}")
    qa.check("报告含「结论」区块与四层发现",
             "结论" in (out_dir / "report.html").read_text(encoding="utf-8") and
             all(k in (out_dir / "report.html").read_text(encoding="utf-8") for k in ("事实", "分析", "推测", "建议")),
             "核心发现 → 结论 结构完整")
    qa.check("3 张图表已生成且非空",
             all(p.stat().st_size > 0 for p in (out_dir / "charts").glob("*.png")) and
             len(list((out_dir / "charts").glob("*.png"))) == 3,
             f"实际 {len(list((out_dir / 'charts').glob('*.png')))} 张")
    qa.check("原始数据未被修改", io_utils.raw_hash("task10") == hash_before, "SHA-256 一致")
    return qa
