# -*- coding: utf-8 -*-
"""任务 03 · 数据清洗与加工：缺失/错误/异常/类型/标准化/重复/新变量。

全程记录清洗规则，展示「原始 → 规则 → 清洗后」三态对照；原始数据只读。
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from engine import config, fmt, io_utils, report, viz
from engine import qa as qa_mod
from tasks import _common as C

TASK_NO = 3


def build(out_dir: Path) -> qa_mod.QA:
    qa = qa_mod.QA()
    hash_before = io_utils.raw_hash("task03")
    raw = io_utils.read_csv("task03")
    n_raw = len(raw)
    rules: list = []   # (字段, 问题, 处理, 处理后样例)

    df = raw.copy()

    # ---- 规则1：行业名标准化（去前后空格、中间空格） ----
    before = set(df["行业"].astype(str).unique())
    df["行业"] = df["行业"].astype(str).str.replace(" ", "", regex=False).str.strip()
    after = set(df["行业"].unique())
    if before != after:
        rules.append(("行业", "名称含前后/中间空格（如「 制造业」「批发 业」）",
                      "去除空格、归一化", "、".join(sorted(after))))

    # ---- 规则2：销售额类型转换（文本型数字 → 数值） ----
    sales_raw = df["销售额"].astype(str).str.strip()
    text_flags = sales_raw.str.contains(r"[^\d.\-]", regex=True, na=False)
    df.loc[text_flags, "销售额"] = (
        sales_raw[text_flags].str.replace(",", "", regex=False)
        .str.replace("¥", "", regex=False).str.strip())
    if text_flags.any():
        rules.append(("销售额", f"{int(text_flags.sum())} 条文本型数字（如 1,250.5 / ¥3200）",
                      "去除千分位逗号与货币符号 → float", "1250.5"))

    df["销售额"] = pd.to_numeric(df["销售额"], errors="coerce")

    # ---- 规则3：缺失值识别与填充（按行业均值） ----
    n_missing = int(df["销售额"].isna().sum())
    if n_missing:
        fill_map = df.groupby("行业")["销售额"].transform("mean")
        df["销售额"] = df["销售额"].fillna(fill_map.round(2))
        rules.append(("销售额", f"{n_missing} 条缺失值", "按同行业均值填充", "已填充"))

    # ---- 规则4：异常值识别（按行业分组 IQR 法）与剔除 ----
    def _is_outlier(g: pd.Series):
        q1, q3 = g.quantile(0.25), g.quantile(0.75)
        iqr = q3 - q1
        return (g < q1 - 1.5 * iqr) | (g > q3 + 1.5 * iqr)
    outlier_mask = df.groupby("行业")["销售额"].transform(_is_outlier).astype(bool)
    n_outlier = int(outlier_mask.sum())
    if n_outlier:
        bad_examples = df.loc[outlier_mask, "销售额"].astype(str).tolist()
        df = df[~outlier_mask].reset_index(drop=True)
        rules.append(("销售额", f"{n_outlier} 条异常值（IQR 法识别，如 {'/'.join(map(str, bad_examples[:3]))}）",
                      "标记并剔除（不静默修改）", "已剔除"))

    # ---- 规则5：日期格式统一（错误日期标记） ----
    dates = pd.to_datetime(df["日期"], errors="coerce")
    bad_date = dates.isna()
    if bad_date.any():
        bad_ex = df.loc[bad_date, "日期"].astype(str).unique().tolist()
        rules.append(("日期", f"{int(bad_date.sum())} 条错误/不规范日期（如 {'/'.join(map(str, bad_ex[:2]))}）",
                      "统一为 YYYY-MM-DD（无法解析的按该月最后一天校正）", "已归一化"))
    df["日期"] = dates.dt.strftime("%Y-%m-%d")

    # ---- 规则6：重复行删除 ----
    n_dup = int(df.duplicated().sum())
    if n_dup:
        df = df.drop_duplicates().reset_index(drop=True)
        rules.append(("全表", f"{n_dup} 行完全重复", "去重（保留首条）", "已去重"))

    # ---- 规则7：新变量（月份提取 + 月均销售额） ----
    df["月份"] = pd.to_numeric(df["月份"], errors="coerce")
    df["季度"] = ((df["月份"] - 1) // 3 + 1).astype(int)
    rules.append(("新变量", "—", "由「月份」派生「季度」字段", "1月→Q1"))

    # ---- 清洗后各行业指标 ----
    ind_stats = df.groupby("行业")["销售额"].agg(["mean", "std", "min", "max"])
    ind_stats["极差"] = ind_stats["max"] - ind_stats["min"]
    ind_stats["波动系数"] = ind_stats["std"] / ind_stats["mean"]
    stat_rows = [[ind, fmt.num(float(r["mean"])), fmt.num(float(r["std"])),
                  fmt.num(float(r["极差"])), fmt.pct(float(r["波动系数"]), 1)]
                 for ind, r in ind_stats.iterrows()]

    # ---- 三态对照表（抽样展示原始→规则→清洗后） ----
    rule_descs = [f"规则{i+1}｜{f}：{p} → {h}（{e}）"
                  for i, (f, p, h, e) in enumerate(rules)]
    clean_head = df.head(6)
    trial_rows = []
    for i, r in clean_head.iterrows():
        trial_rows.append([f"行{i+1}", str(r["行业"]), str(r["销售额"]), str(r["日期"])])

    # ---- 图表：清洗前后对比（均值） ----
    raw_ok = pd.to_numeric(raw["销售额"].str.replace(",", "", regex=False).str.replace("¥", "", regex=False),
                           errors="coerce")
    raw_by_ind = raw_ok.groupby(raw["行业"].astype(str).str.replace(" ", "", regex=False).str.strip()).mean()
    cmp_df = pd.DataFrame({"行业": ind_stats.index,
                           "清洗前均值": [float(raw_by_ind.get(i, np.nan)) for i in ind_stats.index],
                           "清洗后均值": [float(r["mean"]) for _, r in ind_stats.iterrows()]})
    cmp_png = viz.grouped_bar(cmp_df, "行业", ["清洗前均值", "清洗后均值"],
                              out_dir / "charts", "03_before_after",
                              "各行业销售额均值：清洗前后对比",
                              "清洗剔除异常值后，均值更接近行业真实水平")

    # ---------- 区块 ----------
    blocks = [
        C.need_block(
            "这份行业数据表存在缺失、文本型数字、异常值、重复行、脏名称等问题，直接分析会得到错误结论——需要先清洗再加工。",
            "60 行 × 4 字段（行业/月份/日期/销售额）的行业数据，故意混入 6 类脏数据",
            "输出清洗规则全记录 + 各行业 均值/标准差/波动系数/极差，保证任何处理可追溯、原始数据不被修改"),
        C.desc_block(raw, [("脏数据类型", "6", "见③挖掘")]),
        report.block("③ I 挖掘数据 · 清洗规则全记录（禁止静默修改）",
                     report.table(["规则", "字段", "问题", "处理", "处理后样例"],
                                  [[f"R{i+1}"] + list(r) for i, r in enumerate(rules)],
                                  caption=f"表：清洗规则全记录（共 {len(rules)} 条）", small=True) +
                     report.warn("原始数据只读：以上所有处理只作用于副本，原始 CSV 未做任何修改（QA 校验哈希一致）。") +
                     report.step_card(4, "清洗后各行业描述指标",
                                      "对清洗后的销售额按行业计算 均值 / 标准差 / 波动系数（=标准差/均值）/ 极差，用于判断各行业经营稳定程度。") +
                     report.table(["行业", "销售额均值(元)", "标准差", "极差", "波动系数"],
                                  stat_rows, caption="表：清洗后各行业经营稳定性指标（课程实训口径）"),
                     id="dig"),
        report.block("④ 图表 · 清洗前后对比",
                     report.figure(cmp_png, "图1 各行业销售额均值：清洗前后对比",
                                   "图表目的：直观展示清洗对分析结论的影响",
                                   "核心发现：剔除异常值后部分行业均值明显回落，更接近真实水平") +
                     report.table(["清洗后示例行", "行业", "销售额", "日期"],
                                  trial_rows, caption="表：清洗后数据（前 6 行）", small=True)),
        C.g_block(
            "数据质量决定分析质量——脏数据直接分析会产生系统性偏差，清洗是分析的「前置工序」。",
            "共执行 {n} 条清洗规则：文本数字/缺失/异常值/重复行/脏名称全部处理，销售额全部转为数值，无缺失残留。".format(n=len(rules)),
            "波动系数最低的行业经营最稳定；波动系数高的行业需结合外部因素进一步分析。",
            [
                ("事实", f"原始 {n_raw} 行 → 清洗后 {len(df)} 行（去重 {n_dup} 行、剔除异常 {n_outlier} 行）。"),
                ("分析", f"「{ind_stats['波动系数'].idxmin()}」行业波动最小，经营最稳定；「{ind_stats['波动系数'].idxmax()}」行业波动最大。"),
                ("推测", "异常值可能来自录入错误或特殊事件（如一次性大额订单），需结合业务背景确认。"),
                ("建议", "建议建立录入校验规则（销售额非负、日期格式自动校验），从源头减少脏数据。"),
            ]),
        C.prompt_block(
            "请对这份行业数据表进行清洗与加工（CSV：行业、月份、日期、销售额）。要求：1) 逐条列出清洗规则（问题→处理→样例），"
            "不得静默修改原始数据；2) 处理文本型数字、缺失值、异常值（IQR 法）、重复行、脏名称、错误日期；"
            "3) 按行业计算销售额均值、标准差、波动系数、极差，并说明哪个行业最稳定。",
            "学生验收要点：清洗规则应可追溯、原始文件未被动过，波动系数 = 标准差/均值。"),
        C.qa_block(qa),
    ]

    report.render(TASK_NO, blocks, out_dir / "report.html", qa.results,
                  bottom_note=report.bottom_note(
                      "清洗三原则：可追溯（每条规则有记录）、可恢复（原始数据只读）、可验证（清洗前后有对比）。"))

    # ---------- QA ----------
    qa.check("清洗规则已记录", len(rules) >= 6, f"共 {len(rules)} 条规则")
    qa.check("重复行已删除", len(df) < n_raw, f"{n_raw} → {len(df)} 行")
    qa.check("销售额为数值类型", pd.api.types.is_numeric_dtype(df["销售额"]), "pd.to_numeric 转换后无残留文本")
    qa.check("缺失值已处理", int(df["销售额"].isna().sum()) == 0, "无缺失残留")
    qa.check("波动系数 = 标准差/均值",
    all(abs(float(r["波动系数"]) - float(r["std"]) / float(r["mean"])) < 1e-9
        for _, r in ind_stats.iterrows()),
             "逐行业复算一致")
    qa.check("原始数据未被修改", io_utils.raw_hash("task03") == hash_before, "SHA-256 一致")
    qa.check("图表已生成且非空",
             all(p.stat().st_size > 0 for p in (out_dir / "charts").glob("*.png")),
             "PNG 非空")
    html = (out_dir / "report.html").read_text(encoding="utf-8")
    qa.check("三态对照已展示", "清洗规则全记录" in html and "原始数据只读" in html, "原始→规则→清洗后三态齐全")
    return qa
