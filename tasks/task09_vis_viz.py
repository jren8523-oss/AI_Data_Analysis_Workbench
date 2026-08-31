# -*- coding: utf-8 -*-
"""任务 09 · 网店访客数可视化展现：统计表 → 柱/折/饼 → 数据透视表 → 数据透视图。

课程口径：某网店 1 月 1 日至 7 日共 6 个商品类目的每日访客数（长表 42 行），
通过统计表、分类汇总、数据透视表与多种图表展现访客规律。
与任务 01 的区分度：本任务必须包含「排序表 / 分类汇总 / 数据透视表 / 数据透视图」。
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from engine import config, fmt, io_utils, report, viz
from engine import qa as qa_mod
from tasks import _common as C

TASK_NO = 9


def build(out_dir: Path) -> qa_mod.QA:
    qa = qa_mod.QA()
    hash_before = io_utils.raw_hash("task09")
    df = io_utils.read_csv("task09")
    df["日期"] = pd.to_datetime(df["日期"])
    n_days = df["日期"].nunique()

    # ---------- 分析计算（全部确定性代码） ----------
    # 1) 分类汇总：按商品类目汇总（长表 -> 汇总表）
    cat_total = df.groupby("商品类目", as_index=False)["访客数"].sum()
    # 2) 排序表：访客数降序
    cat_total = cat_total.sort_values("访客数", ascending=False).reset_index(drop=True)
    total = int(cat_total["访客数"].sum())
    cat_total["占比"] = cat_total["访客数"] / total
    cat_total["日均"] = cat_total["访客数"] / n_days

    # 按日期汇总（每日总访客）
    day_total = df.groupby("日期", as_index=False)["访客数"].sum()
    day_total["日期"] = day_total["日期"].dt.strftime("%m-%d")
    day_total = day_total.sort_values("日期").reset_index(drop=True)

    # 3) 数据透视表：行 = 日期，列 = 商品类目，值 = 访客数
    pivot = df.pivot_table(index="日期", columns="商品类目", values="访客数",
                           aggfunc="sum", observed=True)
    pivot.index = [d.strftime("%m-%d") for d in pivot.index]
    pivot.index.name = "日期"                              # 保留索引名，reset_index 后列名为"日期"
    pivot = pivot[cat_total["商品类目"].tolist()]           # 列顺序与分类汇总一致
    # 导出透视表 CSV（Excel 直开，UTF-8-sig）
    pivot_path = config.DATA_PROCESSED / "task09_pivot.csv"
    pivot_path.parent.mkdir(parents=True, exist_ok=True)
    pivot.reset_index().to_csv(pivot_path, index=False, encoding="utf-8-sig")

    # 每日最热类目
    daily_top = (df.sort_values("访客数", ascending=False)
                   .groupby("日期").head(1)
                   .sort_values("日期"))
    daily_top["日期"] = daily_top["日期"].dt.strftime("%m-%d")

    # ---------- 图表 ----------
    p1 = viz.bar(cat_total, "商品类目", "访客数", out_dir / "charts", "09_bar",
                 "各商品类目访客数合计（降序排序）", "1 月 1–7 日 · 分类汇总 → 柱形图",
                 sort=True, ylabel="访客数（人次）")
    p2 = viz.line(pivot.reset_index(), "日期", cat_total["商品类目"].tolist(),
                  out_dir / "charts", "09_line",
                  "各商品类目访客数逐日变化", "1 月 1–7 日 · 数据透视表 → 折线图",
                  legend_loc="upper right", ylabel="访客数（人次）")
    p3 = viz.pie(cat_total, "商品类目", "访客数", out_dir / "charts", "09_pie",
                 "各商品类目访客数占比", "1 月 1–7 日 · 分类汇总 → 饼图")
    p4 = viz.grouped_bar(pivot.reset_index(), "日期", cat_total["商品类目"].tolist(),
                         out_dir / "charts", "09_pivot_bar",
                         "数据透视图：每日 × 类目访客数", "行=日期，列=类目，值=访客数",
                         ylabel="访客数（人次）")

    # ---------- 区块 ----------
    pivot_rows = [[idx] + [fmt.num(v, 0) for v in row]
                  for idx, row in pivot.iterrows()]
    blocks = [
        C.need_block(
            "这家网店 1 月 1–7 日各商品类目的访客数有什么规律？哪个类目最受欢迎？周末和工作日有差别吗？",
            "7 天 × 6 类目长表（42 行）：日期 / 商品类目 / 访客数（示例数据按课程描述构造）",
            "用统计表与图表把数据「讲清楚」：分类汇总、排序表、数据透视表、柱形图、折线图、饼图，"
            "并指出类目差异与时间规律"),
        C.desc_block(df, [("日期跨度", "7 天", "2024-01-01 ~ 01-07"), ("商品类目", "6 类", "服装/数码/家居/食品/美妆/图书")]),
        report.block("③ I 挖掘数据 · 统计表（分类汇总 → 排序 → 透视）", "".join([
            report.step_card(1, "分类汇总：长表转汇总表",
                             "对「商品类目」分组求和，得到每个类目 7 天访客合计、日均与占比。"),
            report.table(["排名", "商品类目", "7 日访客合计", "日均访客", "占比"],
                         [[i + 1, r["商品类目"], fmt.num(r["访客数"], 0), fmt.num(r["日均"], 1),
                           fmt.pct(r["占比"], 1)] for i, r in cat_total.iterrows()],
                         caption="表 1 分类汇总排序表（访客数降序）"),
            report.step_card(2, "数据透视表：行=日期，列=类目，值=访客数",
                             "透视表把长表转为二维交叉表，一行是一天、一列是一个类目，"
                             "是后续画「数据透视图」的基础。"),
            report.table(["日期"] + list(pivot.columns), pivot_rows,
                         caption="表 2 数据透视表（已导出 CSV：data/processed/task09_pivot.csv，Excel 可直接打开）", small=True),
            report.step_card(3, "每日总访客与最热类目",
                             "汇总每天全店访客总量，并找出每天访客最多的类目。"),
            report.table(["日期", "全店访客", "当日最热类目", "最热类目访客"],
                         [[r["日期"], fmt.num(day_total.loc[day_total["日期"] == r["日期"], "访客数"].iloc[0], 0),
                           r["商品类目"], fmt.num(r["访客数"], 0)] for _, r in daily_top.iterrows()],
                         caption="表 3 每日汇总与最热类目", small=True),
        ]), id="dig"),
        report.block("④ 图表 · 柱 / 折 / 饼 / 透视图",
                     report.figure(p1, "图1 类目访客合计柱形图（排序）", "直观对比 6 个类目的访客规模",
                                   f"核心发现：{cat_total.iloc[0]['商品类目']} 最高（{fmt.num(cat_total.iloc[0]['访客数'], 0)} 人次），"
                                   f"{cat_total.iloc[-1]['商品类目']} 最低（{fmt.num(cat_total.iloc[-1]['访客数'], 0)} 人次）")
                     + report.figure(p2, "图2 各类目访客逐日折线图", "观察 7 天内的变化趋势与类目间差距",
                                     "核心发现：各线基本平行、波动不大，说明类目格局 7 天内稳定")
                     + report.figure(p3, "图3 类目访客占比饼图", "看结构：前三大类目占全店多少份额",
                                     f"核心发现：前 3 大类目合计占全店 {fmt.pct(sum(cat_total['占比'].head(3)), 1)}")
                     + report.figure(p4, "图4 数据透视图（每日×类目）", "数据透视表的图形化呈现",
                                     "核心发现：全店访客在周末（01-06/01-07）明显抬升")),
        C.g_block(
            "可视化不是「把数字换成图」这么简单：先想清楚要回答什么问题，再选对应的图——比较用柱、趋势用折、结构用饼、交叉看透视。",
            f"7 天全店总访客 {fmt.num(total, 0)} 人次，{cat_total.iloc[0]['商品类目']} 以 {fmt.pct(cat_total.iloc[0]['占比'], 1)} 的份额居首，"
            f"前 3 大类目（{cat_total.iloc[0]['商品类目']}、{cat_total.iloc[1]['商品类目']}、{cat_total.iloc[2]['商品类目']}）占全店 "
            f"{fmt.pct(sum(cat_total['占比'].head(3)), 1)}。",
            f"运营上优先保障头部类目的供给与曝光；周末访客抬升提示可把促销活动排在周六/周日；"
            f"若某类目出现连续下滑，用透视表按月/按周下钻定位原因。",
            [
                ("事实", f"全店访客 {fmt.num(total, 0)} 人次；{cat_total.iloc[0]['商品类目']}（{fmt.pct(cat_total.iloc[0]['占比'], 1)}）、"
                         f"{cat_total.iloc[1]['商品类目']}（{fmt.pct(cat_total.iloc[1]['占比'], 1)}）位列前二。"),
                ("分析", f"周末（01-06/01-07）全店访客高于工作日，两类日平均差约 "
                         f"{fmt.num(day_total['访客数'].tail(2).mean() - day_total['访客数'].head(5).mean(), 0)} 人次。"),
                ("推测", "周末访客抬升符合电商流量规律；头部类目份额高可能与其品类刚需度/首页曝光位有关。"),
                ("建议", "促销与上新尽量安排在周五/周六，吃周末流量红利；对尾部落后的类目排查引流渠道与选品。"),
            ]),
        C.prompt_block(
            "我有一份网店 7 天 × 6 类目的访客数据（CSV：日期、商品类目、访客数，长表 42 行）。请："
            "1) 按类目分类汇总访客数并降序排序，计算占比与日均；2) 制作数据透视表（行=日期，列=类目，值=访客数）；"
            "3) 绘制柱形图、多系列折线图、饼图和数据透视图；4) 指出类目差异与周末/工作日规律。",
            "学生验收要点：必须出现「排序表 + 分类汇总 + 数据透视表 + 数据透视图」四要素；"
            "结论需结合图表给出，不能只罗列数字。"),
        C.qa_block(qa),
    ]

    report.render(TASK_NO, blocks, out_dir / "report.html", qa.results,
                  bottom_note=report.bottom_note(
                      "可视化的链路：统计表（汇总/排序/透视）→ 选对图表（柱/折/饼）→ 交叉透视 → 讲出结论。"))

    # ---------- QA ----------
    qa.check("数据完整（42 = 7 天 × 6 类目）", len(df) == 42 and n_days == 7 and cat_total.shape[0] == 6,
             f"实际 {len(df)} 行 / {n_days} 天 / {cat_total.shape[0]} 类目")
    qa.check("分类汇总复算", qa.approx(cat_total["访客数"].sum(), df["访客数"].sum()),
             f"汇总和 = 原始和 = {fmt.num(total, 0)}")
    qa.check("排序表降序正确",
             all(cat_total["访客数"].iloc[i] >= cat_total["访客数"].iloc[i + 1]
                 for i in range(len(cat_total) - 1)),
             "访客数按降序排列")
    qa.check("占比复算（类目合计 / 全店合计）",
             qa.approx(cat_total["占比"].sum(), 1.0) and
             qa.approx(cat_total["占比"].iloc[0], cat_total["访客数"].iloc[0] / total),
             f"占比合计 = {fmt.pct(cat_total['占比'].sum(), 2)}")
    qa.check("数据透视表形状 (7 行 × 6 类目)", pivot.shape == (7, 6), f"实际 {pivot.shape}")
    qa.check("透视表合计复算", qa.approx(pivot.values.sum(), total),
             f"透视表元素和 = {fmt.num(pivot.values.sum(), 0)}")
    qa.check("透视表 CSV 已导出且非空", pivot_path.exists() and pivot_path.stat().st_size > 0,
             str(pivot_path))
    qa.check("每日合计复算", qa.approx(day_total["访客数"].sum(), total),
             f"每日汇总和 = {fmt.num(day_total['访客数'].sum(), 0)}")
    qa.check("报告含「排序表」「数据透视表」要素（区分任务 01）",
             ("排序" in (out_dir / "report.html").read_text(encoding="utf-8")) and
             ("数据透视表" in (out_dir / "report.html").read_text(encoding="utf-8")),
             "排序表 + 数据透视表已渲染")
    qa.check("4 张图表已生成且非空",
             all(p.stat().st_size > 0 for p in (out_dir / "charts").glob("*.png")) and
             len(list((out_dir / "charts").glob("*.png"))) == 4,
             f"实际 {len(list((out_dir / 'charts').glob('*.png')))} 张")
    qa.check("原始数据未被修改", io_utils.raw_hash("task09") == hash_before, "SHA-256 一致")
    return qa
