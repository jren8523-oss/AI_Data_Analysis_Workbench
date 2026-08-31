# -*- coding: utf-8 -*-
"""任务 07 · 研发与销售关系分析：相关分析 + 一元线性回归 + 预测。

必须出现「相关 ≠ 因果」警示框；预测点 x=15 位于样本范围内（内插）。
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from engine import config, fmt, io_utils, report, stats_corr, viz
from engine import qa as qa_mod
from tasks import _common as C

TASK_NO = 7
PRED_X = 15.0


def build(out_dir: Path) -> qa_mod.QA:
    qa = qa_mod.QA()
    hash_before = io_utils.raw_hash("task07")
    df = io_utils.read_csv("task07")
    x = df["研发投入x(万元)"].astype(float).values
    y = df["销售额y(万元)"].astype(float).values

    corr = stats_corr.correlation(x, y)
    model = stats_corr.linreg(x, y)
    pred = stats_corr.predict(model, PRED_X)

    # ---------- 图表 ----------
    scatter_png = viz.scatter_reg(x, y, out_dir / "charts", "07_scatter",
                                  "研发投入与销售额散点图 + 回归线",
                                  f"r = {corr['r_s']}（{corr['direction']}，{corr['degree']}）",
                                  "研发投入 x（万元）", "销售额 y（万元）",
                                  a=model["a"], b=model["b"],
                                  pred_x=PRED_X, pred_y=float(pred["y0"]))

    # ---------- 区块 ----------
    blocks = [
        C.need_block(
            "研发投入与销售额是否存在线性关系？如果研发投入达到 15 万元，销售额大概能达到多少？",
            "20 次抽样：研发投入 x（万元）与销售额 y（万元），示例数据保证 R² > 0.8",
            "计算相关系数 r（方向+程度）、建立一元线性回归方程 ŷ = a + bx、给出 R² 与 x=15 万元时的预测值，并做因果警示"),
        C.desc_block(df, [("样本量", "20", "次抽样"), ("预测点", "x=15 万元", "位于样本范围内（内插）")]),
        report.block("③ I 挖掘数据 · 相关分析 + 回归分析", "".join([
            report.step_card(1, "相关分析 · 相关系数",
                             "r = Σ(x−x̄)(y−ȳ) / √[Σ(x−x̄)²·Σ(y−ȳ)²]，取值范围 [−1, 1]。"),
            report.formula_box("相关系数 r", corr["formula"], corr["substitution"],
                               corr["r_s"], corr["interpretation"]),
            report.step_card(2, "回归分析 · 最小二乘法",
                             "一元线性回归 ŷ = a + bx，b = Σ(x−x̄)(y−ȳ)/Σ(x−x̄)²，a = ȳ − b·x̄。"),
            report.formula_box("斜率 b", model["b_formula"], model["b_substitution"],
                               model["b_s"], model["b_interpretation"]),
            report.formula_box("截距 a", model["a_formula"], model["a_substitution"],
                               model["a_s"], model["a_interpretation"]),
            report.formula_box("回归方程", "ŷ = a + bx", model["equation"],
                               model["equation"], "回归方程建立完成。"),
            report.formula_box("拟合优度 R²", "R² = 1 − SSE/SST", "（一元回归中 R² = r²）",
                               model["r2_s"], model["r2_interpretation"]),
            report.step_card(3, "预测 · x = 15 万元", "预测点位于样本范围内，属于内插预测。"),
            report.formula_box("预测销售额", pred["formula"], pred["substitution"],
                               pred["y0_s"], pred["interpretation"]),
        ]), id="dig"),
        report.block("④ 图表 · 散点 + 回归线 + 预测点",
                     report.figure(scatter_png, "图1 研发投入与销售额散点图（含回归线与预测点）",
                                   "图表目的：直观展示线性关系强度、方向与预测点位置",
                                   f"核心发现：样本点沿回归线紧密分布（R²={model['r2_s']}），"
                                   f"x=15 万元时预测销售额约 {pred['y0_s']} 万元")),
        C.g_block(
            "相关与回归回答「有没有线性关系、关系有多强、能怎么预测」，但绝不等于「研发导致销售增长」。",
            f"r = {corr['r_s']}，{corr['direction']}、{corr['degree']}；R² = {model['r2_s']}，"
            f"研发投入可解释销售额变动的 {model['r2_s']}；x=15 万元时预测销售额 {pred['y0_s']} 万元。",
            "回归模型可用于销售目标测算，但预测依赖「关系在未来保持稳定」的假设，需定期更新模型。",
            [
                ("事实", f"相关系数 r = {corr['r_s']}，回归方程 {model['equation']}，R² = {model['r2_s']}。"),
                ("分析", f"研发投入每增加 1 万元，销售额平均增加约 {fmt.num(model['b'], 2)} 万元（在样本范围内有效）。"),
                ("推测", "研发可能通过提升产品竞争力间接影响销售，但样本数据无法证明因果关系。"),
                ("建议", "预测值 {pred['y0_s']} 万元可作为预算参考，实际决策还需结合市场、竞品等外部因素。"),
            ]),
        report.block("警示 · 相关 ≠ 因果",
                     report.warn("相关系数与回归系数只能说明统计上的线性关联，不能证明「研发投入」是「销售额增长」的原因。"
                                 "销售额增长可能受市场需求、品牌、渠道等因素共同影响；因果推断需要实验设计或更严格的计量方法，"
                                 "本分析不提供因果结论。"), id="warn"),
        C.prompt_block(
            "这是 20 次抽样数据（CSV：样本编号、研发投入x(万元)、销售额y(万元)）。请："
            "1) 计算相关系数并判断方向与程度；2) 用最小二乘法建立一元线性回归方程 ŷ = a + bx，给出参数含义与 R²；"
            "3) 预测研发投入 15 万元时的销售额；4) 报告中必须明确提示「相关≠因果」，不得把相关关系写成因果关系。",
            "学生验收要点：r 与 R² 数值一致（一元回归 R²=r²）；预测公式 ŷ = a + b×15；因果警示必须出现。"),
        C.qa_block(qa),
    ]

    report.render(TASK_NO, blocks, out_dir / "report.html", qa.results,
                  bottom_note=report.bottom_note(
                      "相关看强弱、回归看规律、预测看落点——但永远记住：统计相关 ≠ 因果关系。"))

    # ---------- QA ----------
    qa.check("−1 ≤ r ≤ 1", -1 <= corr["r"] <= 1, f"r = {corr['r_s']}")
    qa.check("R² ≤ 1 且 > 0.8", 0 < model["r2"] <= 1 and model["r2"] > 0.8,
             f"R² = {model['r2_s']}（示例数据要求 >0.8）")
    qa.check("R² = r²（一元回归）", qa.approx(model["r2"], corr["r"] ** 2),
             f"{model['r2_s']} ≈ {fmt.pct(corr['r'] ** 2, 1)}")
    qa.check("预测点 x=15 在样本范围内", x.min() <= PRED_X <= x.max(),
             f"样本 x 范围 [{fmt.num(float(x.min()), 1)}, {fmt.num(float(x.max()), 1)}]")
    qa.check("预测值复算（手写路径）", qa.approx(pred["y0"], model["a"] + model["b"] * PRED_X),
             f"ŷ = {model['a_s']} + {model['b_s']}×15")
    qa.check("相关≠因果警示必现", "相关 ≠ 因果" in (out_dir / "report.html").read_text(encoding="utf-8"),
             "警示框已渲染")
    qa.check("原始数据未被修改", io_utils.raw_hash("task07") == hash_before, "SHA-256 一致")
    qa.check("图表已生成且非空",
             all(p.stat().st_size > 0 for p in (out_dir / "charts").glob("*.png")),
             "PNG 非空")
    return qa
