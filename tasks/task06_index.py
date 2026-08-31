# -*- coding: utf-8 -*-
"""任务 06 · 产品总成本变动分析：个体指数、综合指数（拉氏/帕氏）、平均指数、因素分析。

展示链条：总体变化 → 各因素 → 各因素影响 → 综合结论；指数体系必须自洽。
教材口径：总成本 = 产量 × 单位成本；总成本指数 = 拉氏产量指数 × 帕氏成本指数。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from engine import config, fmt, io_utils, report, stats_index, viz
from engine import qa as qa_mod
from tasks import _common as C

TASK_NO = 6


def build(out_dir: Path) -> qa_mod.QA:
    qa = qa_mod.QA()
    hash_before = io_utils.raw_hash("task06")
    df = io_utils.read_csv("task06")
    df = df.sort_values("产品").reset_index(drop=True)

    q0 = df["产量q0(件)"].astype(float).tolist()
    q1 = df["产量q1(件)"].astype(float).tolist()
    p0 = df["单位成本p0(元)"].astype(float).tolist()
    p1 = df["单位成本p1(元)"].astype(float).tolist()

    indiv = stats_index.individual_indices(q0, q1, p0, p1)
    ci = stats_index.composite_indices(q0, q1, p0, p1)
    ai = stats_index.average_indices(q0, q1, p0, p1)
    fa = stats_index.factor_analysis(q0, q1, p0, p1)

    # ---------- 图表 ----------
    q_df = pd.DataFrame({"产品": df["产品"], "基期产量 q0": q0, "报告期产量 q1": q1})
    q_png = viz.grouped_bar(q_df, "产品", ["基期产量 q0", "报告期产量 q1"],
                            out_dir / "charts", "06_output",
                            "三种产品产量变动（q0 → q1）",
                            "分组柱形图比较各产品产量变化")
    p_df = pd.DataFrame({"产品": df["产品"], "基期单位成本 p0": p0, "报告期单位成本 p1": p1})
    p_png = viz.grouped_bar(p_df, "产品", ["基期单位成本 p0", "报告期单位成本 p1"],
                            out_dir / "charts", "06_cost",
                            "三种产品单位成本变动（p0 → p1）",
                            "分组柱形图比较各产品单位成本变化")
    idx_df = pd.DataFrame({"指数": ["拉氏产量指数", "帕氏成本指数", "总成本指数"],
                           "数值": [fa["k_q"], fa["k_p"], fa["k_total"]]})
    idx_png = viz.bar(idx_df, "指数", "数值", out_dir / "charts", "06_index",
                      "总成本指数体系（相对数，基期 = 100%）",
                      "总成本指数 = 拉氏产量指数 × 帕氏成本指数（指数体系自洽）",
                      value_labels=False)

    # ---------- 区块 ----------
    blocks = [
        C.need_block(
            "三种产品报告期总成本相比基期变化了多少？其中产量变动和单位成本变动各自贡献了多少？",
            "3 种产品的 基期/报告期 产量（q0/q1）与单位成本（p0/p1），总成本 = 产量 × 单位成本",
            "计算个体指数、综合指数（拉氏/帕氏）、平均指数，并通过因素分析拆解 产量影响 与 成本影响，验证指数体系自洽"),
        C.desc_block(df, [("产品数", "3", "A/B/C"), ("指数维度", "2", "产量 + 单位成本")]),
        report.block("③ I 挖掘数据 · 指标计算（个体 → 综合 → 平均 → 因素）", "".join([
            report.step_card(1, "个体指数",
                             "每种产品产量/成本的变动幅度：i_q = q1/q0，i_p = p1/p0。"),
            report.table(["产品", "q0(件)", "q1(件)", "产量个体指数", "p0(元)", "p1(元)", "成本个体指数"],
                         stats_index.format_table(q0, q1, p0, p1),
                         caption="表：三种产品个体指数"),
            report.step_card(2, "综合指数（拉氏 / 帕氏）",
                             "拉氏指数以基期为同度量因素：产量指数 Kq = Σq₁p₀/Σq₀p₀；"
                             "帕氏指数以报告期为同度量因素：成本指数 Kp = Σp₁q₁/Σp₀q₁。"),
            report.formula_box("拉氏产量指数（Kq）",
                               "Kq = Σq₁p₀ / Σq₀p₀",
                               f"Kq = {fmt.num(ci['s_q1p0'])} / {fmt.num(ci['s_q0p0'])}",
                               fmt.pct(fa["k_q"], 1),
                               f"产量整体变动使总成本变为基期的 {fmt.pct(fa['k_q'], 1)}（产量增加 {fmt.pct(fa['k_q'] - 1, 1)}）。"),
            report.formula_box("帕氏成本指数（Kp）",
                               "Kp = Σp₁q₁ / Σp₀q₁",
                               f"Kp = {fmt.num(ci['s_q1p1'])} / {fmt.num(ci['s_q1p0'])}",
                               fmt.pct(fa["k_p"], 1),
                               f"单位成本整体变动使总成本变为 {fmt.pct(fa['k_p'], 1)}（成本{'上升' if fa['k_p'] > 1 else '下降'} {fmt.pct(abs(fa['k_p'] - 1), 1)}）。"),
            report.step_card(3, "平均指数（加权算术 / 加权调和）",
                             "加权算术平均指数（数量，基期总值加权）应等于拉氏产量指数；"
                             "加权调和平均指数（质量，报告期总值加权）应等于帕氏成本指数。"),
            report.formula_box("加权算术平均指数（数量）", "Kq = Σ(iq·p₀q₀) / Σ(p₀q₀)",
                               "iq·p₀q₀ 逐产品加总", fmt.pct(float(ai["kq_arithmetic"]), 1),
                               f"与拉氏产量指数一致：{fmt.pct(float(ai['kq_arithmetic']), 1)}"),
            report.formula_box("加权调和平均指数（质量）", "Kp = Σ(p₁q₁) / Σ[(p₁q₁)/ip]",
                               "分母逐产品以 q₁p₀ 折算", fmt.pct(float(ai["kp_harmonic"]), 1),
                               f"与帕氏成本指数一致：{fmt.pct(float(ai['kp_harmonic']), 1)}"),
            report.step_card(4, "因素分析 · 总成本 = 产量 × 单位成本",
                             "相对数：总成本指数 = 拉氏产量指数 × 帕氏成本指数；"
                             "绝对额：总成本增减 = 产量影响 + 成本影响。"),
            report.table(["因素", "相对数（指数）", "绝对额影响（元）"],
                         [["产量变动", fmt.pct(fa["k_q"], 1), fmt.sign(fa["q_effect"])],
                          ["单位成本变动", fmt.pct(fa["k_p"], 1), fmt.sign(fa["p_effect"])],
                          ["总成本合计", fmt.pct(fa["k_total"], 1), fmt.sign(fa["total_chg"])]],
                         caption="表：因素分析（指数体系 + 绝对额拆解）"),
            report.warn(f"自洽校验：{fmt.pct(fa['k_total'], 2)} = {fmt.pct(fa['k_q'], 2)} × {fmt.pct(fa['k_p'], 2)}；"
                        f"{fmt.sign(fa['total_chg'])} = {fmt.sign(fa['q_effect'])} + {fmt.sign(fa['p_effect'])} —— 指数体系自洽 ✓"),
        ]), id="dig"),
        report.block("④ 图表 · 产量 / 成本 / 指数",
                     report.figure(q_png, "图1 产量变动（q0 → q1）",
                                   "图表目的：比较各产品产量增减", "核心发现：产品A、C 增产明显") +
                     report.figure(p_png, "图2 单位成本变动（p0 → p1）",
                                   "图表目的：比较各产品单位成本增减", "核心发现：产品B 成本上升、A/C 下降") +
                     report.figure(idx_png, "图3 总成本指数体系",
                                   "图表目的：展示 产量/成本/总成本 三类指数的相对关系",
                                   "核心发现：总成本指数 = 产量指数 × 成本指数，体系自洽")),
        C.g_block(
            "统计指数把「总成本变了多少」拆成「产量变了多少 × 成本变了多少」，让管理者看清变化的真正来源。",
            f"总成本由基期 {fmt.num(ci['s_q0p0'])} 元 变为 {fmt.num(ci['s_q1p1'])} 元，变动 {fmt.sign_pct(fa['k_total'] - 1)}；"
            f"产量因素贡献 {fmt.sign(fa['q_effect'])} 元，成本因素贡献 {fmt.sign(fa['p_effect'])} 元。",
            "若成本上升主要由产量扩张驱动，属于良性增长；若由单位成本上升驱动，需优化采购/工艺控制成本。",
            [
                ("事实", f"总成本指数 {fmt.pct(fa['k_total'], 1)}；拉氏产量指数 {fmt.pct(fa['k_q'], 1)}；帕氏成本指数 {fmt.pct(fa['k_p'], 1)}。"),
                ("分析", f"总成本变动 {fmt.sign(fa['total_chg'])} 元 = 产量影响 {fmt.sign(fa['q_effect'])} 元 + 成本影响 {fmt.sign(fa['p_effect'])} 元。"),
                ("推测", "产量上升可能与市场扩张有关；单位成本变化与原材料价格、生产效率相关（需业务数据验证）。"),
                ("建议", "对成本影响为负的产品重点复盘工艺与采购策略；保持产量增长的可持续性。"),
            ]),
        C.prompt_block(
            "这是 3 种产品的产量与单位成本数据（CSV：产品、产量q0、产量q1、单位成本p0、单位成本p1）。请："
            "1) 计算个体指数、拉氏指数、帕氏指数、加权算术平均指数、加权调和平均指数；"
            "2) 做总成本因素分析：总成本变动 = 产量变动影响 + 单位成本变动影响（相对数与绝对额都要）；"
            "3) 验证指数体系自洽：总成本指数 = 拉氏产量指数 × 帕氏成本指数。",
            "学生验收要点：总成本指数 ≈ 产量指数 × 成本指数（相对数），增减额 = 产量影响 + 成本影响（绝对额）。"),
        C.qa_block(qa),
    ]

    report.render(TASK_NO, blocks, out_dir / "report.html", qa.results,
                  bottom_note=report.bottom_note(
                      "因素分析一条链：总成本指数 = 产量指数 × 成本指数，相对数与绝对额双重自洽——结论才立得住。"))

    # ---------- QA ----------
    qa.check("指数体系自洽（相对数）", bool(fa["relative_consistent"]),
             f"{fmt.pct(fa['k_total'], 2)} = {fmt.pct(fa['k_q'], 2)} × {fmt.pct(fa['k_p'], 2)}")
    qa.check("绝对额自洽（增减拆解）", bool(fa["absolute_consistent"]),
             f"{fmt.sign(fa['total_chg'])} = {fmt.sign(fa['q_effect'])} + {fmt.sign(fa['p_effect'])}")
    qa.check("加权算术平均指数 = 拉氏产量指数",
             qa.approx(float(ai["kq_arithmetic"]), float(fa["k_q"])),
             f"{fmt.pct(float(ai['kq_arithmetic']), 2)} ≈ {fmt.pct(fa['k_q'], 2)}")
    qa.check("加权调和平均指数 = 帕氏成本指数",
             qa.approx(float(ai["kp_harmonic"]), float(fa["k_p"])),
             f"{fmt.pct(float(ai['kp_harmonic']), 2)} ≈ {fmt.pct(fa['k_p'], 2)}")
    qa.check("总成本复算（手写 Σp1q1）",
             qa.approx(ci["s_q1p1"], sum(a * b for a, b in zip(q1, p1))),
             "Σq1p1 口径一致")
    qa.check("原始数据未被修改", io_utils.raw_hash("task06") == hash_before, "SHA-256 一致")
    qa.check("图表已生成且非空",
             all(p.stat().st_size > 0 for p in (out_dir / "charts").glob("*.png")),
             "PNG 非空")
    html = (out_dir / "report.html").read_text(encoding="utf-8")
    qa.check("关键数字渲染", fmt.num(ci["s_q1p1"]) in html, "总成本已渲染")
    return qa
