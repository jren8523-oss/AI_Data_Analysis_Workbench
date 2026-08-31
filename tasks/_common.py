# -*- coding: utf-8 -*-
"""任务脚本公共组件：数据概况块、需求块。所有任务脚本共用，保持区块风格统一。"""
from __future__ import annotations

import pandas as pd

from engine import describe, fmt, report


def need_block(question: str, data_src: str, want: str) -> str:
    """① 需求块：一句话业务问题 + 数据来源 + 希望的结果。"""
    body = f"""
    <div class="step-card"><div class="step-num step-num-q">Q</div><div class="step-body">
      <div class="step-title">要回答的业务问题</div><div class="step-text">{question}</div></div></div>
    <div class="step-card"><div class="step-num step-num-d">D</div><div class="step-body">
      <div class="step-title">数据来源</div><div class="step-text">{data_src}</div></div></div>
    <div class="step-card"><div class="step-num step-num-g">G</div><div class="step-body">
      <div class="step-title">希望的结果</div><div class="step-text">{want}</div></div></div>
    """
    return report.block("① 需求 · 先明确问题，再动手分析（DIG 起点）", body, id="need")


def desc_block(df: pd.DataFrame, extra_metrics: list | None = None) -> str:
    """② D 描述数据 块：规模 / 字段 / 类型 / 缺失 / 唯一值 / 示例行。"""
    d = describe.describe(df)
    metrics = [("记录数", fmt.num(d["n_rows"], 0), "行"), ("字段数", str(d["n_cols"]), "列")]
    if extra_metrics:
        metrics += extra_metrics
    body = report.metric_grid(metrics)
    rows = [[c["name"], c["dtype"], c["missing"], fmt.pct(c["missing_pct"]),
             c["nunique"], c["sample"]] for c in d["columns"]]
    body += report.table(["字段", "类型", "缺失", "缺失率", "唯一值", "样例"], rows,
                         caption="表：数据字段概况（Describe 结果）")
    # 示例行
    head_rows = d["head"]
    if head_rows:
        body += report.table(d["head_cols"], head_rows, caption="表：数据示例（前 5 行）", small=True)
    if d["issues"]:
        body += report.warn("；".join(d["issues"]))
    return report.block("② D 描述数据 · 先理解数据，再分析", body, id="describe")


def g_block(blocks_html: str, why: str, what: str, how: str, extra_findings: list | None = None) -> str:
    """⑤ G 给出产出 块：Why→What→How + 分层结论（事实/分析/推测/建议）。"""
    body = report.dig_cards([
        ("WHY", "为什么重要", why),
        ("WHAT", "数据告诉我们什么", what),
        ("HOW", "怎么用 / 怎么优化", how),
    ])
    if extra_findings:
        for level, title, text in extra_findings:
            body += report.finding(level, title, text)
    return report.block("⑤ G 给出产出 · 分层结论（事实 / 分析 / 推测 / 建议）", body, id="goal")


def prompt_block(prompt: str, note: str = "") -> str:
    """⑥ 推荐 Prompt 块。"""
    return report.block("⑥ 推荐 Prompt · 学生可复制后自行用 AI 复现同款分析",
                        report.prompt_box(prompt, note), id="prompt")


def qa_block(qa_obj) -> str:
    """⑦ QA 验证块。"""
    return report.block("⑦ QA 验证 · 数值复算 / 逻辑检查 / 输出一致性",
                        report.qa_block(qa_obj.results), id="qa")
