# -*- coding: utf-8 -*-
"""任务 01 · 店铺访客数分析：对比分析 / 趋势分析 / 占比分析（柱/折/饼）。

三种分析思维各配一张图；环比增速体现「昨天没做完自动滚到今天」的对比视角。
只调引擎，不写算法。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from engine import config, fmt, io_utils, report, viz
from engine import qa as qa_mod
from tasks import _common as C

TASK_NO = 1


def build(out_dir: Path) -> qa_mod.QA:
    qa = qa_mod.QA()
    hash_before = io_utils.raw_hash("task01")
    df = io_utils.read_csv("task01")

    src_cols = ["直接访问", "搜索引擎", "社交媒体", "外部链接", "广告投放"]
    df[src_cols] = df[src_cols].astype(float)
    df["总访客数"] = df[src_cols].sum(axis=1).round(0).astype(int)

    # ---------- 指标 ----------
    total = float(df["总访客数"].sum())
    monthly_mean = float(df["总访客数"].mean())
    peak_idx = int(df["总访客数"].idxmax())
    peak_month, peak_val = df.loc[peak_idx, "月份"], float(df.loc[peak_idx, "总访客数"])

    shares = df[src_cols].sum() / total
    share_rows = [[s, fmt.num(float(v), 0), fmt.pct(float(v) / total)]
                  for s, v in shares.items()]

    mom = df["总访客数"].pct_change()
    mom_rows = []
    for i, r in df.iterrows():
        prev = df["总访客数"].iloc[i - 1] if i > 0 else None
        mom_rows.append([r["月份"], fmt.num(float(r["总访客数"]), 0),
                         "—" if prev is None else fmt.sign_pct(mom.iloc[i])])

    # ---------- 图表 ----------
    bar_png = viz.bar(df, "月份", "总访客数", out_dir / "charts", "01_monthly_total",
                      "店铺各月总访客数（对比分析）",
                      "柱形图适合比较各月的绝对水平，一眼看出哪个月最高/最低",
                      value_labels=True)
    line_png = viz.line(df, "月份", ["总访客数"], out_dir / "charts", "01_trend",
                        "店铺访客数趋势（趋势分析）",
                        "折线图展示随时间的变化方向与速度",
                        annotate_last=("总访客数", f"{peak_month} 峰值 {fmt.num(peak_val, 0)}"))
    pie_df = pd.DataFrame({"来源": shares.index, "访客数": shares.values * total})
    pie_png = viz.pie(pie_df, "来源", "访客数", out_dir / "charts", "01_share",
                      "店铺访客来源占比（占比分析）",
                      "饼图直观展示各来源对总访客的贡献份额")

    # ---------- 区块 ----------
    blocks = [
        C.need_block(
            "这家店铺的访客情况如何？哪些月份表现好？访客主要来自哪些渠道？",
            "店铺全年 12 个月的访客数据：5 个来源渠道（直接访问/搜索引擎/社交媒体/外部链接/广告投放）与总访客数",
            "得到 对比（各月高低）→ 趋势（变化方向）→ 占比（渠道贡献）三张图与结论，支撑运营决策"),
        C.desc_block(df, [("月份跨度", "12", "1月~12月"), ("来源渠道", "5", "类目")]),
        report.block("③ I 挖掘数据 · 指标计算（对比 / 趋势 / 占比）", "".join([
            report.metric_grid([
                ("全年总访客", fmt.num(total, 0), "12 个月合计"),
                ("月度均值", fmt.num(monthly_mean, 0), "平均每月访客"),
                ("峰值月份", f"{peak_month}", f"{fmt.num(peak_val, 0)} 人次"),
                ("最高占比渠道", str(shares.idxmax()), fmt.pct(float(shares.max()))),
            ]),
            report.step_card(1, "对比分析 · 各月总访客高低",
                             f"全年总访客 {fmt.num(total, 0)} 人次，峰值出现在 {peak_month}（{fmt.num(peak_val, 0)} 人次），"
                             f"最低月与峰值月差距明显——对比分析回答「谁高谁低」。"),
            report.step_card(2, "趋势分析 · 环比增速",
                             "环比增速 = (本月 − 上月) / 上月 × 100%，反映逐月变化方向与力度（见下表）。"
                             "增长最快的月份与促销/活动节点往往对应。"),
            report.step_card(3, "占比分析 · 渠道贡献",
                             f"访客主要来自「{shares.idxmax()}」渠道（占 {fmt.pct(float(shares.max()))}），"
                             f"占比结构决定投放资源应向哪里倾斜。"),
            report.table(["月份", "总访客数", "环比增速"], mom_rows,
                         caption="表：各月总访客数与环比增速（趋势分析依据）", small=True),
            report.table(["来源渠道", "访客数", "占比"], share_rows,
                         caption="表：访客来源占比（占比分析依据）", small=True),
        ]), id="dig"),
        report.block("④ 图表 · 三种分析思维各配一张图",
                     report.figure(bar_png, "图1 各月总访客数柱形图（对比分析）",
                                   "图表目的：比较各月访客绝对水平，识别高低点",
                                   "核心发现：全年呈上升趋势，11 月达到峰值") +
                     report.figure(line_png, "图2 访客趋势折线图（趋势分析）",
                                   "图表目的：展示时间维度上的变化方向与速度",
                                   "核心发现：整体上行、年末加速，说明店铺处于成长期") +
                     report.figure(pie_png, "图3 访客来源占比饼图（占比分析）",
                                   "图表目的：展示各渠道对总访客的贡献份额",
                                   f"核心发现：{shares.idxmax()} 是最大流量来源（{fmt.pct(float(shares.max()))}）")),
        C.g_block(
            "访客是店铺运营的基础指标，先搞清楚「量有多大、从哪来、往哪走」才能决定资源投入。",
            "全年访客 {total} 人次、月度均值 {mean} 人次；{peak} 月最高；{top} 渠道贡献 {top_pct} 的流量。".format(
                total=fmt.num(total, 0), mean=fmt.num(monthly_mean, 0),
                peak=peak_month, top=shares.idxmax(), top_pct=fmt.pct(float(shares.max()))),
            "运营上应巩固 {top} 渠道，同时加大社交媒体/外部链接的投入（目前占比较低，增长空间大）；"
            "参照 {peak} 月的成功经验安排下一次活动节奏。".format(top=shares.idxmax(), peak=peak_month),
            [
                ("事实", "全年总访客 {total} 人次；{peak} 月为峰值（{peak_val} 人次）；{top} 渠道占比 {top_pct}。".format(
                    total=fmt.num(total, 0), peak=peak_month, peak_val=fmt.num(peak_val, 0),
                    top=shares.idxmax(), top_pct=fmt.pct(float(shares.max())))),
                ("分析", "访客整体呈上升趋势且年末加速，说明店铺正处于成长期；流量来源高度集中于单一渠道，存在结构性风险。"),
                ("推测", "11 月峰值可能与促销活动有关（数据未含活动标记，需结合运营日历验证）。"),
                ("建议", "保持现有渠道优势的同时，测试投放低占比渠道；建立「访客数 × 转化率」联动监控。"),
            ]),
        C.prompt_block(
            "请帮我分析这份店铺访客数据（Excel/CSV：月份、直接访问、搜索引擎、社交媒体、外部链接、广告投放、总访客数）。"
            "要求：1) 计算全年总访客、月度均值、峰值月份、环比增速；2) 用柱形图做各月对比、折线图做趋势、饼图做来源占比；"
            "3) 给出事实、分析、建议三层的结论，不超过 300 字。",
            "学生验收要点：报告应包含 对比/趋势/占比 三类图，且环比增速、峰值月份与这份标准答案一致。"),
        C.qa_block(qa),
    ]

    report.render(TASK_NO, blocks, out_dir / "report.html", qa.results,
                  bottom_note=report.bottom_note(
                      "一图一思维：柱形图看高低、折线图看方向、饼图看结构——选对图，结论自然清晰。"))

    # ---------- QA ----------
    qa.check("数据规模", len(df) == 12, f"12 个月数据（实际 {len(df)} 行）")
    qa.check("总访客 = 各渠道之和",
             qa.approx(df["总访客数"].sum(), df[src_cols].sum().sum()),
             "所有行总访客列与各渠道加总一致")
    qa.check("占比合计 = 100%", qa.approx(shares.sum(), 1.0), f"来源占比合计 {fmt.pct(float(shares.sum()))}")
    mom_ok = all(abs(m - (df['总访客数'].iloc[i] / df['总访客数'].iloc[i-1] - 1)) < 1e-9
                 for i, m in enumerate(mom[1:], start=1) if not pd.isna(m))
    qa.check("环比增速复算（不同代码路径）", mom_ok, "环比 = 本月/上月 − 1，逐月核对一致")
    qa.check("原始数据未被修改", io_utils.raw_hash("task01") == hash_before, "SHA-256 一致")
    qa.check("图表已生成且非空",
             all(png.stat().st_size > 0 for png in (out_dir / "charts").glob("*.png")),
             f"{len(list((out_dir/'charts').glob('*.png')))} 张 PNG 非空")
    html = (out_dir / "report.html").read_text(encoding="utf-8")
    qa.check("关键数字出现在报告", fmt.num(total, 0) in html or fmt.num(monthly_mean, 0) in html,
             "总访客/月度均值已渲染")
    qa.check("task01 专属元素（环比+三思维）",
             ("环比" in html) and ("对比分析" in html) and ("趋势分析" in html) and ("占比分析" in html),
             "报告含环比增速与三种分析思维对照")
    return qa
