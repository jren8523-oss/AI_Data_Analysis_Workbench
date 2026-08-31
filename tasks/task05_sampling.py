# -*- coding: utf-8 -*-
"""任务 05 · 小区居民用电分析：大样本总体均值/比例区间估计（95% 置信水平）。

展示完整链条：输入 → 统计量 → 公式 → 计算过程 → 结果 → 解释。
课程口径：随机抽取 100 户，95% 置信水平，z=1.96。
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from engine import config, fmt, io_utils, report, stats_infer, viz
from engine import qa as qa_mod
from tasks import _common as C

TASK_NO = 5


def build(out_dir: Path) -> qa_mod.QA:
    qa = qa_mod.QA()
    hash_before = io_utils.raw_hash("task05")
    df = io_utils.read_csv("task05")
    x = df["月电费(元)"].astype(float)

    n = len(x)
    n_gt80 = int((x > 80).sum())
    p_hat = n_gt80 / n

    mi = stats_infer.mean_interval(x, conf=0.95, z=stats_infer.Z_95)
    pi = stats_infer.proportion_interval(p_hat, n, conf=0.95, z=stats_infer.Z_95)

    # ---------- 图表 ----------
    hist_png = viz.hist_box(x.values, out_dir / "charts", "05_hist",
                            "100 户居民月电费分布",
                            "月电费箱线图",
                            bins=10, xlabel="月电费（元）",
                            mean_val=float(mi["mean"]["value"]),
                            ci_lower=float(mi["lower"]), ci_upper=float(mi["upper"]))
    pie_df = pd.DataFrame({"类别": ["电费 > 80 元", "电费 ≤ 80 元"],
                           "户数": [n_gt80, n - n_gt80]})
    pie_png = viz.pie(pie_df, "类别", "户数", out_dir / "charts", "05_prop",
                      "样本中电费高于 80 元的户数占比",
                      f"p̂ = {n_gt80}/{n} = {fmt.pct(p_hat)}")

    # ---------- 区块 ----------
    chain_html = report.step_card(1, "输入 · 样本数据", f"随机抽取 {n} 户居民，月电费样本数据（户号 + 月电费(元)）") + \
        report.step_card(2, "统计量 · 样本特征", report.metric_grid([
            ("样本量 n", str(n), "大样本判定 n≥30"),
            ("样本均值 x̄", mi["mean"]["value_s"], "元"),
            ("样本标准差 s", mi["std"]["value_s"], "元"),
            ("高于 80 元的户数", str(n_gt80), f"样本比例 p̂ = {fmt.pct(p_hat)}"),
        ])) + \
        report.step_card(3, "公式 · 区间估计口径",
                         "总体均值：x̄ ± z·(s/√n)；总体比例：p̂ ± z·√[p̂(1−p̂)/n]；95% 置信水平 z=1.96")

    blocks = [
        C.need_block(
            "这 100 户居民的电费数据，能否推断整个小区的月电费水平？电费高于 80 元的居民占多大比例？",
            "随机抽取 100 户居民月电费（元），示例数据按课程描述构造（约 30–40% 户高于 80 元）",
            "在 95% 置信水平下给出 ①所有居民月电费均值的置信区间 ②电费高于 80 元居民比例的置信区间，并展示完整计算过程"),
        C.desc_block(df, [("样本量", "100", "户"), (">80 元户数", str(n_gt80), f"占比 {fmt.pct(p_hat)}")]),
        report.block("③ I 挖掘数据 · 输入 → 统计量 → 公式 → 过程 → 结果",
                     chain_html +
                     report.formula_box("总体均值区间估计", mi["interval"]["formula"],
                                         mi["interval"]["substitution"],
                                         f"[{fmt.num(float(mi['lower']))} 元, {fmt.num(float(mi['upper']))} 元]",
                                         mi["interval"]["interpretation"]) +
                     report.formula_box("总体比例区间估计", pi["interval"]["formula"],
                                         pi["interval"]["substitution"],
                                         f"[{fmt.pct(float(pi['lower']), 1)}, {fmt.pct(float(pi['upper']), 1)}]",
                                         pi["interval"]["interpretation"]) +
                     report.warn(f"大样本判定：n = {n} ≥ 30，可用 z 分布近似；"
                                 f"比例区间检验：np̂ = {n_gt80} 且 n(1−p̂) = {n - n_gt80}，均 ≥ 5，近似条件满足。"),
                     id="dig"),
        report.block("④ 图表 · 分布与比例",
                     report.figure(hist_png, "图1 月电费分布直方图（含均值线与 95% 置信区间）",
                                   "图表目的：展示数据分布 + 直观看到置信区间位置",
                                   f"核心发现：分布右偏，均值 x̄={fmt.num(float(mi['mean']['value']))} 元，"
                                   f"95% 置信区间 [{fmt.num(float(mi['lower']))}, {fmt.num(float(mi['upper']))}] 元") +
                     report.figure(pie_png, "图2 电费高于 80 元的户数占比",
                                   "图表目的：展示样本比例 p̂",
                                   f"核心发现：{n_gt80} 户（{fmt.pct(p_hat)}）月电费高于 80 元")),
        C.g_block(
            "抽样估计的意义：用样本推断总体，并给出推断的可靠程度（置信区间 + 置信水平），而不是拍脑袋给一个点。",
            f"95% 置信水平下，小区居民月电费均值区间为 [{fmt.num(float(mi['lower']))} 元, {fmt.num(float(mi['upper']))} 元]；"
            f"电费高于 80 元的比例区间为 [{fmt.pct(float(pi['lower']), 1)}, {fmt.pct(float(pi['upper']), 1)}]。",
            "若需更精确的估计（更窄的区间），可增加样本量；也可据此制定电费补贴、节能宣传等政策。",
            [
                ("事实", f"样本均值 {fmt.num(float(mi['mean']['value']))} 元，样本标准差 {fmt.num(float(mi['std']['value']))} 元；"
                         f"{n_gt80} 户（{fmt.pct(p_hat)}）高于 80 元。"),
                ("分析", f"均值区间 [{fmt.num(float(mi['lower']))}, {fmt.num(float(mi['upper']))}] 元表明：若重复抽样，"
                         f"约 95% 的区间会覆盖总体真实均值。"),
                ("推测", "部分家庭电费明显偏高（右尾），可能与取暖/人口规模有关，需补充家庭特征数据验证。"),
                ("建议", "对高用电群体（>80 元）重点关注，可结合峰谷电价政策引导错峰用电。"),
            ]),
        C.prompt_block(
            "这是 100 户居民月电费的抽样数据（CSV：户号、月电费(元)）。请在 95% 置信水平（z=1.96）下："
            "1) 估计所有居民月电费均值的置信区间；2) 估计电费高于 80 元居民比例的置信区间；"
            "3) 展示计算过程：统计量 → 公式 → 代入 → 结果 → 解释；4) 说明大样本判定条件。",
            "学生验收要点：均值区间 = x̄ ± 1.96·(s/√100)；比例区间 = p̂ ± 1.96·√[p̂(1−p̂)/100]，与标准答案一致。"),
        C.qa_block(qa),
    ]

    report.render(TASK_NO, blocks, out_dir / "report.html", qa.results,
                  bottom_note=report.bottom_note(
                      "区间估计三要素：点估计（样本统计量）、允许误差（z·SE）、置信水平（95%）——三者构成完整结论。"))

    # ---------- QA ----------
    qa.check("样本量 n = 100", n == 100, f"实际 {n} 户")
    qa.check("z = 1.96（95% 置信水平）", qa.approx(stats_infer.Z_95, 1.96), "课程指定值")
    qa.check("均值区间 lower < upper", float(mi["lower"]) < float(mi["upper"]),
             f"[{fmt.num(float(mi['lower']))}, {fmt.num(float(mi['upper']))}]")
    qa.check("比例区间在 [0,1] 内", 0 <= float(pi["lower"]) <= float(pi["upper"]) <= 1,
             f"[{fmt.pct(float(pi['lower']), 1)}, {fmt.pct(float(pi['upper']), 1)}]")
    qa.check("样本比例 30–40% 口径", 0.30 <= p_hat <= 0.40, f"p̂ = {fmt.pct(p_hat)}")
    qa.check("均值区间复算（手写路径）",
             qa.approx(float(mi["lower"]), float(x.mean() - 1.96 * x.std(ddof=1) / np.sqrt(n))),
             "lower = x̄ − 1.96·s/√n")
    qa.check("原始数据未被修改", io_utils.raw_hash("task05") == hash_before, "SHA-256 一致")
    qa.check("图表已生成且非空",
             all(p.stat().st_size > 0 for p in (out_dir / "charts").glob("*.png")),
             "PNG 非空")
    html = (out_dir / "report.html").read_text(encoding="utf-8")
    qa.check("完整链条已展示",
             all(k in html for k in ["输入", "统计量", "公式", "结果", "解释"]),
             "输入→统计量→公式→过程→结果→解释齐全")
    return qa
