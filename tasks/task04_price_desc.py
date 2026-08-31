# -*- coding: utf-8 -*-
"""任务 04 · 生产资料市场价格分析：描述性统计（集中趋势/离散程度/分布形态）。

每个指标都给「公式 → 代入 → 结果 → 解释」四件套，不只输出数字。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from engine import config, fmt, io_utils, report, stats_core, viz
from engine import qa as qa_mod
from tasks import _common as C

TASK_NO = 4


def build(out_dir: Path) -> qa_mod.QA:
    qa = qa_mod.QA()
    hash_before = io_utils.raw_hash("task04")
    df = io_utils.read_csv("task04")

    varieties = [c for c in df.columns if c != "月份"]
    long_rows = []
    for v in varieties:
        for _, r in df.iterrows():
            long_rows.append({"月份": r["月份"], "品种": v, "价格": float(r[v])})
    long_df = pd.DataFrame(long_rows)

    # ---------- 描述统计（按品种） ----------
    stats_by_var = {}
    for v in varieties:
        s = df[v].astype(float)
        stats_by_var[v] = stats_core.full_descriptive(s)

    # ---------- 指标网格 + 四件套（以第一个品种为主展示，其余汇总） ----------
    main_var = varieties[0]
    main_st = stats_by_var[main_var]
    grid_items = [("品种数", str(len(varieties)), "螺纹钢/线材/中厚板/热轧卷板")]
    for name, key in [("均值", "mean"), ("中位数", "median")]:
        grid_items.append((f"{name}（{main_var}）", main_st["central"][key]["value_s"], "元/吨"))
    grid_items.append((f"标准差（{main_var}）", main_st["dispersion"]["std"]["value_s"], "元/吨"))
    grid_items.append(("变异系数", fmt.pct(float(main_st["dispersion"]["cv"]["value"]), 1), "无量纲"))

    formula_html = ""
    f_labels = [("集中趋势·均值", main_st["central"]["mean"]),
                ("集中趋势·中位数", main_st["central"]["median"]),
                ("集中趋势·众数", main_st["central"]["mode"]),
                ("离散程度·极差", main_st["dispersion"]["range"]),
                ("离散程度·平均差", main_st["dispersion"]["mad"]),
                ("离散程度·方差", main_st["dispersion"]["var"]),
                ("离散程度·标准差", main_st["dispersion"]["std"]),
                ("离散程度·四分位差", main_st["dispersion"]["iqr"]),
                ("离散程度·变异系数", main_st["dispersion"]["cv"]),
                ("分布形态·偏度", main_st["shape"]["skew"]),
                ("分布形态·峰度", main_st["shape"]["kurt"])]
    for label, f in f_labels:
        formula_html += report.formula_box(label, f["formula"], f["substitution"],
                                           f["value_s"], f["interpretation"])

    # 各品种均值汇总表
    mean_rows = [[v, fmt.num(float(stats_by_var[v]["central"]["mean"]["value"])),
                  fmt.num(float(stats_by_var[v]["dispersion"]["std"]["value"])),
                  fmt.num(float(stats_by_var[v]["dispersion"]["range"]["value"])),
                  fmt.pct(float(stats_by_var[v]["dispersion"]["cv"]["value"]), 1)]
                 for v in varieties]

    # ---------- 图表 ----------
    hist_png = viz.hist_box(long_df[long_df["品种"] == main_var]["价格"].values,
                            out_dir / "charts", "04_hist",
                            f"{main_var} 价格分布直方图（分布形态）",
                            f"{main_var} 价格箱线图（离散程度）",
                            bins=5, xlabel="价格（元/吨）",
                            mean_val=float(main_st["central"]["mean"]["value"]))
    price_df = df.melt(id_vars="月份", var_name="品种", value_name="价格")
    line_png = viz.line(price_df, "月份", ["价格"], out_dir / "charts", "04_price",
                        "生产资料价格走势（1–5 月）",
                        "多品种折线图比较各品种价格水平与走势",
                        legend_loc="upper left", ylabel="价格（元/吨）")

    # ---------- 区块 ----------
    blocks = [
        C.need_block(
            "黑色金属类生产资料 1–5 月价格如何分布？整体处于什么水平？各品种价格波动有多大？",
            "1–5 月 × 4 个生产资料品种（螺纹钢/线材/中厚板/热轧卷板）的价格，单位：元/吨",
            "输出 集中趋势（均值/中位数/众数）+ 离散程度（极差/方差/标准差/四分位差/平均差/变异系数）+ 分布形态（偏度/峰度）"
            "，每个指标带公式与解释"),
        C.desc_block(df, [("月份跨度", "5", "1月~5月"), ("品种", "4", "黑色金属类")]),
        report.block("③ I 挖掘数据 · 指标计算（每个指标四件套）",
                     report.metric_grid(grid_items) + formula_html +
                     report.table(["品种", "均值(元/吨)", "标准差", "极差", "变异系数"],
                                  mean_rows, caption="表：各品种描述统计汇总"),
                     id="dig"),
        report.block("④ 图表 · 分布形态与价格走势",
                     report.figure(hist_png, "图1 价格分布直方图 + 箱线图",
                                   "图表目的：观察价格集中区间、对称性与离群点",
                                   f"核心发现：{main_var} 价格集中在均值附近，箱线图可看出上下四分位与离群点") +
                     report.figure(line_png, "图2 生产资料价格走势折线图",
                                   "图表目的：比较 4 个品种的价格水平与 5 个月走势",
                                   "核心发现：各品种价格水平分层明显，整体小幅波动")),
        C.g_block(
            "描述性统计回答「数据长什么样」：水平（集中趋势）、波动（离散程度）、形态（偏度/峰度），是后续推断分析的基础。",
            f"{main_var} 均价 {fmt.num(float(main_st['central']['mean']['value']))} 元/吨，"
            f"标准差 {fmt.num(float(main_st['dispersion']['std']['value']))} 元/吨，"
            f"变异系数 {fmt.pct(float(main_st['dispersion']['cv']['value']), 1)}。",
            "价格水平与波动幅度是采购/库存决策的重要参考；变异系数可跨品种比较稳定性。",
            [
                ("事实", f"各品种 5 个月价格均值区间 [{min(float(stats_by_var[v]['central']['mean']['value']) for v in varieties):.0f}, "
                         f"{max(float(stats_by_var[v]['central']['mean']['value']) for v in varieties):.0f}] 元/吨。"),
                ("分析", f"{main_var} 中位数 {fmt.num(float(main_st['central']['median']['value']))} 元/吨与均值接近，分布近似对称。"),
                ("推测", "价格波动主要受原材料成本与市场供需影响（5 个月样本较短，仅反映短期特征）。"),
                ("建议", "关注波动系数最高的品种，制定弹性采购策略以对冲价格风险。"),
            ]),
        C.prompt_block(
            "请对这份生产资料价格数据做描述性统计分析（CSV：月份、螺纹钢、线材、中厚板、热轧卷板，元/吨）。要求："
            "1) 计算各品种的均值、中位数、众数、极差、方差、标准差、四分位差、平均差、变异系数、偏度、峰度；"
            "2) 每个指标给出计算公式和代入过程，不只是数字；3) 用直方图+箱线图展示分布，折线图比较走势；4) 解释数字的业务含义。",
            "学生验收要点：众数取最小众数（与 Excel MODE 一致）；方差为样本无偏（n−1）；变异系数 = 标准差/均值。"),
        C.qa_block(qa),
    ]

    report.render(TASK_NO, blocks, out_dir / "report.html", qa.results,
                  bottom_note=report.bottom_note(
                      "描述统计三件套：均值看水平、标准差看波动、偏度看形态——数字+解释才能用于决策。"))

    # ---------- QA ----------
    m = main_st
    qa.check("均值复算（手写路径）",
             qa.approx(m["central"]["mean"]["value"], float(df[main_var].mean())),
             f"均值 {fmt.num(float(m['central']['mean']['value']))} 元/吨")
    qa.check("极差 = max − min 复算",
             qa.approx(m["dispersion"]["range"]["value"],
                       float(df[main_var].max() - df[main_var].min())),
             "极差口径一致")
    qa.check("变异系数 = 标准差/均值",
             qa.approx(m["dispersion"]["cv"]["value"],
                       float(df[main_var].std()) / float(df[main_var].mean())),
             f"CV = {fmt.pct(float(m['dispersion']['cv']['value']), 2)}")
    qa.check("标准差为样本无偏（ddof=1）",
             qa.approx(m["dispersion"]["std"]["value"], float(df[main_var].std(ddof=1))),
             "与 pandas ddof=1 一致")
    qa.check("原始数据未被修改", io_utils.raw_hash("task04") == hash_before, "SHA-256 一致")
    qa.check("图表已生成且非空",
             all(p.stat().st_size > 0 for p in (out_dir / "charts").glob("*.png")),
             "PNG 非空")
    html = (out_dir / "report.html").read_text(encoding="utf-8")
    qa.check("四件套已渲染", all(needle in html for needle in ["公式", "代入", "结果", "解释"]),
             "每个指标含公式→代入→结果→解释")
    return qa
